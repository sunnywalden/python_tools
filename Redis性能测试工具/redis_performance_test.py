#!/usr/bin/python
#-*- coding:utf8 -*-

import os,subprocess
import re
import time
import sys

test_cmd = '/opt/redis/bin/redis-benchmark -h 0.0.0.0 -p ' + sys.argv[1] + ' -n ' + sys.argv[2] + ' -r ' + sys.argv[3] + ' --dbnum 1  -t get,set,lpush,lpop -c ' + sys.argv[4] + ' -q'

def redis_per_test():

	res = []
	#p = subprocess.Popen(test_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#returncode = p.poll()
	#while returncode is None:
        #	line = p.stdout.readline()
        #	returncode = p.poll()
	#	time.sleep(1)
        #	line = line.strip()
	r = os.popen(test_cmd)
	info = r.readlines()
	for line in info:
		line = line.strip()
		print(line)

		res_juage = re.search(r'(?:[1-9]\d+\.\d+) requests per second',line)
		#print(res_juage)
		if res_juage:
			result = res_juage.group()
			print('debug performance test data:',result)
			adr_res_time = re.search(r'[1-9]\d+\.\d+',result)
			if adr_res_time:
				res_time = adr_res_time.group()
				if res_time:
					print('performance data final:',res_time) 
					#for tm in res_time:
					#res.append(tm)
					res.append(res_time)
	print(res)
	return res
        #res = p.stdout.readlines()
        #print('debug test response:',res)
	#os.exit(0)

def get_avg_performance():
	all_res = []
	avg_res = {}
	n = 10
	all_set_res,all_get_res,all_lpush_res,all_lpop_res = 0.0,0.0,0.0,0.0

	for a in range(n):
		res = redis_per_test()
		#set_res = res[0]
		#get_res = res[1]
		#lpush_res = res[2]
		#lpop_res = res[3]
		all_res.append(res)
		time.sleep(6)
	for res in all_res:
		all_set_res += float(res[0])
		all_get_res += float(res[1])
		all_lpush_res += float(res[2])
		all_lpop_res += float(res[3])
			
	avg_res['set_res'] = float('%.2f' % (all_set_res / n))
	avg_res['get_res'] = float('%.2f' % (all_get_res / n))
	avg_res['lpush_res'] = float('%.2f' % (all_lpush_res / n))
	avg_res['lpop_res'] = float('%.2f' % (all_lpop_res / n))
	print(avg_res)	

if __name__ == '__main__':
	#redis_per_test()
	get_avg_performance()

