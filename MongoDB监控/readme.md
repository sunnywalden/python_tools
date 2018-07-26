一、概述

本项目用于对MongoDB集群进行监控，包括mongo实例的服务状态、是否为master、队列长度、使用内存大小、连接数等指标。


二、部署

主要包括监控采集脚本部署及zabbix模板的配置。

2.1 脚本部署

2.1.1 mongo连接信息修改
a.需要根据实际环境情况，修改mongo实例的地址和端口号。
if __name__ == '__main__':
    mongodb_27002 = MongoDB('ip1', port1)
    mongodb_27003 = MongoDB('ip2', port2)
    mongodb_27004 = MongoDB('ip3', port3)
    sent_metrics(mongodb_27002)
    sent_metrics(mongodb_27003)
    sent_metrics(mongodb_27004)


b.如果有认证，请修改init函数部分的用户信息
        self.mongo_user = None
        self.mongo_password = None


c.部署脚本
     将此脚本上传到待监控主机的/usr/local/zabbix/plugin路径

d.设置cron定时任务



2.2 上传zabbix模板

2.2.1 模板上传

进入zabbix模板管理页面：http://zabbixserver:port/zabbix/templates.php?ddreset=1。

点击导入，浏览并找到项目中的模板文件，完成导入。

2.2.2 模板配置

修改模板名称，添加需要监控的主机，根据需要修改应用集、监控项及触发器、图形的名称等配置项。

3.查看效果
进入zabbix-检测中-最新数据,选择主机，确认是否成功获取到检测项的数据
