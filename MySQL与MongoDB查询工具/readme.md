一、功能概述

首先查询MongoDB和MySQL，得到MongoDB库中conDisplayType字段与MySQLpartition中的值。然后对比，找出MongoDB中存在而MySQL分区中缺失的值。最后在MySQL表中新增分区。

二、数据源详情

mongodb：
	10.200.26.29
	migu_video库中program集合
源字段：
	contDisplayType字段
MySQL：
	migu_video库metadata表
目标字段：
PARTITION BY LIST (contDisplayType)
