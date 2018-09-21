#-*- coding:utf-8 -*-

from base.log import logger
from base.opt import *
import redis
from config  import GET_CONF
from param import *
import sys
import item_redis
import time
import scorer
import redis_pool
import counter

DEFINE_FLAG("-r", "--raw_data", dest = "raw_data", default = 'data/raw_data.txt')
DEFINE_FLAG("-k", "--skip_first_line", dest = "skip_first_line", default = False, action="store_true")

class Reader():

    def process_line(self, line):
        segs = line.split('\t')
        if 12 != len(segs):
            logger().warning('error line[%s]', line)
            counter.inc('error line')
            return
        
        data = {}
        data['content_id'] = segs[0]
        data['program_id'] = segs[1]
        data['pack_id'] = segs[2]
        data['hits'] = segs[3]
        data['cont_name'] = segs[4]

        data['cont_recomm'] = segs[5]
        data['publish_time'] = segs[6]
        data['cont_type'] = segs[7]
        data['cont_type_name'] = segs[8]
        data['media_shape'] = segs[9]
        
        data['keywords'] = segs[10]
        data['source'] = segs[11]
        self.process(data)

    def process(self, data):
        pass

    def post_process(self):
        pass

    def run(self):
        fpath = FLAG().raw_data
        if not fpath:
            logger().error('bad raw_data path[%s]', fpath)
            sys.exit(1)
        logger().info('raw_data path[%s]', fpath)
        cnt = 0
        '''
        first_line = True
        '''
        # for line in open(fpath, 'rU'):
        for line in open(fpath):
            '''
            if first_line:
                first_line = False
                if FLAG().skip_first_line:
                    continue
            # not first_line
            '''
            self.process_line(line.strip())
        self.post_process()




def main():
    Reader().run()


if __name__ == '__main__':
    main()
