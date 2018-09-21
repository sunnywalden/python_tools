#!/bin/bash
echo 'use demo; \
SELECT \
  name,sex,account \
from \
  student \
where \
  account in ("1001", "1002") \
  and name not in ("张三", "李四") \
' | \
mysql -h192.168.1.10 -udemo -p"**********" -N

