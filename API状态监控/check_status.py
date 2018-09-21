#!/usr/bin/python
# coding=utf-8

import requests
import json
from zabbix_helper import send_to_zabbix_server

DOMAIN_STATISTICS = "http://localhost:7070/monitor?mode=status"
PATH_STATISTICS = "http://localhost:7070/monitor?mode=action&delete=false"
NORMAL_STATUS_CODES = ("200", "301", "302")


def get_failed_code_rate(host_data):
    normal = 0
    total = 0
    for code in host_data.keys():
        total += host_data[code]["count"]
        if code in NORMAL_STATUS_CODES:
            normal += host_data[code]["count"]
    print "count :",total
    print "normal:",normal

    if total > 0:
        failed_rate = 1.0 - normal / float(total)
    else:
        failed_rate = 0.0
    print "failed_rate:", failed_rate

    return failed_rate


def get_failed_code_rate2(host_data):
    normal = 0
    total = 0
    for code in host_data.keys():
        for num in host_data[code]:
            total += host_data[code][num]["count"]
            if code in NORMAL_STATUS_CODES:
                normal += host_data[code][num]["count"]

    if total > 0:
        failed_rate = 1.0 - normal / float(total)
    else:
        failed_rate = 0.0

    return failed_rate


def get_long_tail_rate(host_data):
    total = 0
    long_tail = 0
    for code in host_data.keys():
        total += host_data[code]["count"]
        long_tail += host_data[code]["long_tail_count"]

    long_tail_rate = long_tail / float(total)
    return long_tail_rate


def get_long_tail_rate2(host_data):
    total = 0
    long_tail = 0
    for code in host_data.keys():
        for num in host_data[code]:
            total += host_data[code][num]["count"]
            long_tail += host_data[code][num]["long_tail_count"]

    long_tail_rate = long_tail / float(total)
    return long_tail_rate


def get_avg_request_time(host_data):
    count = 0
    success_req_time = 0.0

    for code in host_data.keys():
        count += host_data[code]["count"]
        if code in NORMAL_STATUS_CODES:
            success_req_time += host_data[code]['avg_req_time'] * host_data[code]["count"]

    avg_req_time = success_req_time / count
    return avg_req_time


def get_avg_request_time2(host_data):
    count = 0
    success_req_time = 0.0

    for code in host_data.keys():
        for num in host_data[code]:
            count += host_data[code][num]["count"]
            if code in NORMAL_STATUS_CODES:
                success_req_time += host_data[code][num]['avg_req_time'] * host_data[code][num]["count"]

    avg_req_time = success_req_time / count
    return avg_req_time


def check_domain_status_rate():
    r = requests.get(DOMAIN_STATISTICS)
    print r.content
    if r.status_code != requests.codes.ok:
        send_to_zabbix_server('api.check_normal_status.failed', 1)
        return

    data = json.loads(r.content)
    for host in data:
        failed_rate = get_failed_code_rate(data[host])
        metric = 'api.domain.%s.failed_code_rate' % host.replace('.', '_')
        send_to_zabbix_server(metric, failed_rate)

        long_tail_rate = get_long_tail_rate(data[host])
        metric = 'api.domain.%s.long_tail_rate' % host.strip('.').replace('.', '_')
        send_to_zabbix_server(metric, long_tail_rate)

        avg_req_time = get_avg_request_time(data[host])
        metric = 'api.domain.%s.avg_req_time' % host.strip('.').replace('.', '_')
        send_to_zabbix_server(metric, avg_req_time)

def check_path_status_rate():
    r = requests.get(PATH_STATISTICS)
    print r.content
    if r.status_code != requests.codes.ok:
        send_to_zabbix_server('api.check_normal_status.failed', 1)
        return

    data = json.loads(r.content)
    if "feed_api.migu.com" in data:
        d1 = data["demo_api.demo.com"]
        #path = "/api/recommend/demo"
        for path in d1.keys():
            for num in d1[path]:
                failed_rate = get_failed_code_rate2(d1[path])
                metric = 'api.path.%s.failed_code_rate' % path.strip('/').replace('/', '_')
                send_to_zabbix_server(metric, failed_rate)

                long_tail_rate = get_long_tail_rate2(d1[path])
                metric = 'api.path.%s.long_tail_rate' % path.strip('/').replace('/', '_')
                send_to_zabbix_server(metric, long_tail_rate)

                avg_req_time = get_avg_request_time2(d1[path])
                metric = 'api.path.%s.avg_req_time' % path.strip('/').replace('/', '_')
                send_to_zabbix_server(metric, avg_req_time)


if __name__ == "__main__":
    # the call order cannot be reverted
    check_path_status_rate()

    check_domain_status_rate()
