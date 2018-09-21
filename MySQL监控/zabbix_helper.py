#!/usr/bin/python

import os
import sys

ZABBIX_SENDER = "/usr/local/zabbix/bin/zabbix_sender"
ZABBIX_SERVER_ADDR = "192.168.1.128"

def send_to_zabbix_server(metric, value):
    host = get_host()
    # shell cmd: /usr/local/zabbix/bin/zabbix_sender -z server_addr -s hostname -k metric -o value
    cmd = "%s -z %s -s %s -k %s -o %s" % (ZABBIX_SENDER, ZABBIX_SERVER_ADDR, host, metric, value)
    print "debug: host:", host, "metric:", metric, "value:", value
    ret = os.popen(cmd)
    debug_str = ret.read()
    print "debug:", debug_str
    return debug_str


def check_process(cmd, metric):
    ret = os.popen(cmd)
    value = int(ret.read())
    if value > 0:
        value = 0 
    else:
        value = 1 
    send_to_zabbix_server(metric, value)


def get_host():
    # shell cmd: /usr/local/zabbix/sbin/zabbix_agentd -t agent.hostname | sed -n 's/.*|\(.*\)]/\1/p'"
    cmd = "/usr/local/zabbix/sbin/zabbix_agentd -t agent.hostname | sed -n 's/.*|\(.*\)]/\\1/p'"
    ret = os.popen(cmd)
    return ret.read().strip()


def usage():
    print "%s <metric> <value>" % os.path.basename(sys.argv[0])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    send_to_zabbix_server(sys.argv[1], sys.argv[2])

