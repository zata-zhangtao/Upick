

import asyncio
from src.utils.contentSummary import get_website_summary

### 1. 用户登录

# 有一个用户类

from src.services import User
zata = User("zata")
print(zata.get_subscription())

### 2. 用户查看所有订阅的网站的内容

sub_list = zata.get_content_of_subscription()

print(sub_list)


### 3. 使用agent总结所有网站的内容


summary = asyncio.run(get_website_summary(str(sub_list))) 

print(summary)





