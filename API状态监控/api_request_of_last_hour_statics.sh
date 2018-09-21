#!/usr/bin/bash

host=`/usr/local/zabbix/sbin/zabbix_agentd -t agent.hostname | sed -n 's/.*|\(.*\)]/\1/p'`

demo_log_dir='/data/logs/nginx/demo/'
day=`date +%Y%m%d_`
h=`date +%H`
file_time=`date +%Y%m%d_%H -d  '-1 hours'`
last_h=`expr $h - 1`
file_date=${day}'*'${last_h}
demo_file=`find ${demo_log_dir} -name access_${file_time}*.log`

demo_words='/api/recommend/demo'

demo_sum=`grep "$demo_words" ${demo_file}|wc -l`

echo '************************************************'
date +"%Y%m%d %H:%M:%S"
echo $demo_sum


/usr/local/zabbix/bin/zabbix_sender -z 192.168.1.10 -s $host -k demo_api_requests -o $demo_sum

echo '************************************************'
