<h2 id="install">安装使用</h2>



### conda install
1. 将本项目下载并解压
2. 进入项目路径，然后使用一些命令进行安装(需要提前安装conda, 3.10 <= python version <= 3.12)
```bash
conda create -n Upick python=3.11
conda activate Upick
pip install -r requirements.txt
python run.py
```

### windows exe




### 使用建议

1. 如果使用智谱AI免费模型，建议使用GLM-Z1-Flash，其他的几个我试了，几乎处于不可用状态
2. 如果配置文件yaml中想要设置为None，直接空着就行，如果填None反而是字符串的'None'