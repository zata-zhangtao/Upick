# 遇到的问题
1. 直接把apikey写在config文件里面的方式不安全，最好可以把apikey写在环境变量里面，但是metaGPT加载配置文件的时候不能处理${ZHIPUAI_API_KEY} 这样的环境变量


