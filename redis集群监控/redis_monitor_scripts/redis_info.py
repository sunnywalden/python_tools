#!/usr/bin/env python
#-*- coding:utf-8 -*-

import redis, argparse

class Metric(object):
    def __init__(self, host, key, value, clock = None):
        self.host = host
        self.key = key
        self.value = value
        self.clock = clock

    def __repr__(self):
        if self.clock is None:
            result = 'Metric(%r, %r, %r)' % (self.host, self.key, self.value)
        else:
            result = 'Metric(%r, %r, %r, %r)' % (self.host, self.key, self.value, self.clock)

        return result

def parse_args():
    parser = argparse.ArgumentParser(description = 'Redis status script')
    parser.add_argument('--host', default = 'localhost',
                        help = 'redis host, default localhost')
    parser.add_argument('--port', default = 6379, type = int,
                        help = 'redis port, default 6379')
    parser.add_argument('--pswd', default = None,
                        help = 'redis password')
    parser.add_argument('metric', nargs = '?', help = 'redis metric name')
    parser.add_argument('db', nargs = '?', help = 'redis db name')

    return parser.parse_args()

def get_redis_info(args):
    client = redis.StrictRedis(host = args.host, port = args.port, password = args.pswd)
    server_info = client.info()

    if args.metric:
        try:
            print(server_info[args.metric])
        except KeyError:
            print("Cannot find Key %s" % args.metric)
    else:
        a = []
        for i in server_info:
            a.append(Metric(args.host, ('redis[%s]' % i), server_info[i]))

        llensum = 0
        for key in client.scan_iter('*'):
            if client.type(key) == 'list':
                llensum += client.llen(key)
        a.append(Metric(args.host, 'redis[llenall]', llensum))

        print(a)

def main():
    args = parse_args()

    return get_redis_info(args)

if __name__ == '__main__':
    main()
