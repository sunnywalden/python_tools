#!/usr/bin/python
#-*- encoding: utf8 -*-

from datetime import date, timedelta
import glob
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import socket

import urllib2
import json
import codecs

LOG_PATHS = {'demo api': '/data/logs/nginx/demo/'}

dont_send = True


def handle_log(log, total_c, total_r):

    codes = {}
    response_times = {}
    with open(log, 'r') as f:
        for line in f:
            tline = line
	    if tline.find('/api/recommend/demo') < 0:
                pass
            else:
		if tline.find('client_id= - -/') >= 0:
		    pass
		else:
                    fields = tline.split()
                    nfields = fields[1]
                    if nfields in response_times:
                        response_times[nfields] += 1
                    else:
                        response_times[nfields] = 1

                    if fields[3] in codes:
                        codes[fields[3]] += 1
                    else:
                        codes[fields[3]] = 1

        for c in codes:
            if c in total_c:
                total_c[c] += codes[c]
            else:
                total_c[c] = codes[c]

        for r in response_times:
            if r in total_r:
                total_r[r] += response_times[r]
            else:
                total_r[r] = response_times[r]

    hour = log[-10:-8]
    codes = sorted(codes.items(), key=lambda x: float(x[0]))

    code_data = ''
    for v in codes:
        line = str(v[0] + ": " + str(v[1]) + "\n")
        code_data += line

    if not code_data:
        code_data = '<center>-</center>'

    sum_time = 0.0
    sum_count = 0.0
    long_tail_count = 0.0
    long_tail_200_count = 0.0

    for k, v in response_times.items():
        minseconds = float(k)
        count = float(v)
        sum_time += minseconds * count
        sum_count += count
        if minseconds >= 1.0:
            long_tail_count += count
        if minseconds >= 0.2:
            long_tail_200_count += count

    avg_resp_time = '<center>-</center>'
    long_tail_rate = '<center>-</center>'
    long_tail_200_rate = '<center>-</center>'
    if sum_count != 0.0:
        avg_resp_time = '%.3fms' % (sum_time / sum_count)
        avg_resp_time = '%.3fms' % (sum_time / sum_count * 1000.0)
        long_tail_200_rate = '%.3f%%' % (long_tail_200_count / sum_count * 100.0)
        long_tail_rate = '%.3f%%' % (long_tail_count / sum_count * 100.0)
#        long_tail_rate = '%.3f%%' % (long_tail_count / sum_count)
#        long_tail_200_rate = '%.3f%%' % (long_tail_200_count / sum_count)

    return hour, avg_resp_time, long_tail_rate, long_tail_200_rate, code_data


def get_logs(day, path):
    pattern = path + "/" + "access_" + day + "*"
    
    files = glob.glob(pattern)
    files.sort()
    return files


def report_total_statistics(total_c, total_r):
    global dont_send

    total_c_tmp = sorted(total_c.items(), key=lambda x: float(x[0]))
    code_data = ''
    for v in total_c_tmp:
        line = str(v[0]) + ": " + str(v[1]) + "\n"
        code_data += line

    if not code_data:
        code_data = '<center>-</center>'

    sum_time = 0.0
    sum_count = 0.0
    long_tail_count = 0.0
    long_tail_200_count = 0.0
    for k, v in total_r.items():
        minseconds = float(k)
        count = float(v)
        sum_time += minseconds * count
        sum_count += count
        if minseconds >= 1.0:
            long_tail_count += count
        if minseconds >= 0.2:
            long_tail_200_count += count

    avg_resp_time = '<center>-</center>'
    long_tail_rate = '<center>-</center>'
    long_tail_200_rate = '<center>-</center>'
    if sum_count != 0.0:
        dont_send = False
        avg_resp_time = '%.3fms' % (sum_time / sum_count * 1000)
        long_tail_rate = '%.3f%%' % (long_tail_count / sum_count * 100.0)
        long_tail_200_rate = '%.3f%%' % (long_tail_200_count / sum_count * 100.0)

    return avg_resp_time, long_tail_rate, long_tail_200_rate, code_data


def get_html(service, log_path, hour_data1, total_data1, hour_data2, total_data2):
    html = ''
    html += '<p>业务：%s</p>' % service
    html += '<p>日志路径：%s</p>' % log_path

    html += '<table border="1">'
    html += '<tr><th></th><th>平均响应时间</th><th>响应码统计</th><th>长尾响应(1s)响应率</th><th>长尾响应(200ms)响应率</th>' + '<th> VS </th>' +\
        '<th>前一天平均响应时间</th><th>前一天响应码统计</th><th>前一天长尾响应(1s)响应率</th><th>长尾响应(200ms)响应率</th></tr>'

    html += '<tr><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td></tr>'\
            % ('全天', total_data1[0], total_data1[3], total_data1[1], total_data1[2], total_data2[0], total_data2[3], total_data2[1], total_data1[2])

    i = 0
    for quadruplet in hour_data1:
        #html += '<tr><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td>' % (quadruplet[0], quadruplet[1], quadruplet[3], quadruplet[2])
        html += '<tr><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td>' % (quadruplet[0], quadruplet[1], quadruplet[4], quadruplet[2], quadruplet[3])
        try:
            v = hour_data2[i]
            if quadruplet[0] == v[0]:
                html += '<td></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td><td><center>%s</center></td></tr>' % (v[1], v[4], v[2], v[3])
        except:
            html += '<td></td><td><center>-</center></td><td><center>-</center></td><td><center>-</center></td></tr>'
        i += 1
    html += '</table>'
    return html

def send_mail(html):
    receivers = ['shanghai@cloudin.cn','huangfuxin@cloudin.cn','caobei@cloudin.cn']

    html = '<p>主机：%s</p><p></p>' % socket.gethostname() + html
    msg = MIMEText(html, 'html', 'utf8')

def http_post(html):
    url = 'http://10.200.26.14:5000/sendmail'
    log_time = (date.today() - timedelta(1)).strftime("%Y年%m月%d日")
    html = '<p>主机：%s</p><p></p>' % socket.gethostname() + html
    receivers = ['shanghai@cloudin.cn', 'sangyongjia@migu.cn']
    fromer = 'no-reply-devops@cloudin.cn'

    data = {'smtpserver': {'server': 'smtp.exmail.qq.com', 'mailuser': 'no-reply-devops@cloudin.cn', 'mailpasswd': 'migu1qaz!QAZ'},
            'emailsubject': {'subject': '统计结果：' + log_time + 'demo服务状态统计', 'mess': html},
            'receivesuser': {'receiver': receivers},
            'fromuser': {'fromer': fromer}}
 
    headers = {'Content-Type': 'application/json'}
    req = urllib2.Request(url=url, headers=headers, data=json.dumps(data))
    response = urllib2.urlopen(req)
    return response.read()

def main():
    yesterday = (date.today() - timedelta(1)).strftime("%Y%m%d")
    the_day_before = (date.today() - timedelta(2)).strftime("%Y%m%d")

    html = ''
    for service, log_path in LOG_PATHS.items():
        total_r = {}
        total_c = {}

        files1 = get_logs(yesterday, log_path)
        hour_data1 = []
        for f in files1:
            hour_data1.append(handle_log(f, total_c, total_r))

        total_data1 = report_total_statistics(total_c, total_r)

        total_r = {}
        total_c = {}
        files2 = get_logs(the_day_before, log_path)
        hour_data2 = []
        for f in files2:
            hour_data2.append(handle_log(f, total_c, total_r))

        total_data2 = report_total_statistics(total_c, total_r)

        html += get_html(service, log_path, hour_data1, total_data1, hour_data2, total_data2)

    if not dont_send:
        http_post(html)
        print 'send!'

if __name__ == '__main__':
    main()
