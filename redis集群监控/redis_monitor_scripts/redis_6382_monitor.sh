#!/bin/bash

dir_name=$(dirname $0)
cnf_file=$dir_name/redis_6382_conf.sh
test -s $cnf_file && . $cnf_file
cmd_prefix="python $dir_name/redis_info.py --host $host --port $port --pswd $passwd"

zabbix_server=10.200.56.126
host=$(/usr/local/zabbix/sbin/zabbix_agentd -t agent.hostname | sed -n 's/.*|\(.*\)]/\1/p')
log_file=/var/log/monitor_redis_6382.log

LOG() {
    echo "$(date +'%F %T') $@" >> $log_file
}

monitor_redis() {
    case $1 in
        connected_clients|used_memory|role)
            val=$($cmd_prefix $1)
            LOG "$1 = $val"

            /usr/local/zabbix/bin/zabbix_sender -z $zabbix_server -s $host -k redis_6382.$1 -o $val
            ;;
        *)
            printf "Usage:\n\t$0 connected_clients|used_memory|role\n"
            exit 1
    esac
}

monitor_items=(connected_clients used_memory role)
for item in ${monitor_items[@]}
do
    monitor_redis $item
done
