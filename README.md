1、参考各个仓库， 最后只用到：139cloud.py  （没有用13cloud22 和 main.py。 各个py文件有仓库来源，main.py就是此fork仓库的上游。）
2、环境变量：  名：ydypCK   值：完整Authorization值#手机号#token值       第①部分包括Basic，第③部分token值为00即可。多账号换行或者“@”分开
             wx pushplus推送：名：PUSHPLUS  值：自己token
3、已开启Actions定时运行 。（后方read也来自上游，暂未用到）
4、本地phones格式：手机号，换行Authorization值，经过formatToken换成标准环境变量的secret。test


5、asign.config.mjs是另一个js签到脚本的，经过addJSToken.py（不完美）处理phones.txt（格式：手机换行Basictoken，所有号码）后，得到的纯token（但不能直接用，只能复制里面token拷贝使用）
拷贝这些token到D:\caiyun-0.5.4\tools\asign.config.mjs中，并上传该文件到gcp-hk的/root/caiyun_sign目录中。gcphk定时运行。








![caiyun-autosign](https://socialify.git.ci/unify-z/caiyun-autosign/image?description=1&language=1&name=1&owner=1&theme=Auto)
## 📖 介绍
基于 Python 的中国移动云盘（原和彩云）自动签到程序

## 📚 使用方法
### 1. 安装环境
确保已拥有 Python 和 pip 环境。如果未安装，请参考 [Python 官方文档](https://www.python.org/downloads/) 进行安装。

### 2. 安装依赖库
在终端中执行以下命令，安装所需的 Python 库：
```bash
pip install -r requirements.txt
```
### 3. 准备工作
1. 准备文件夹

    在云盘选择或新建一个文件夹，用于后续操作。

2. 获取认证信息

    参考 [AList 官方文档](https://alist.nn.ci/zh/guide/drivers/139.html#%E6%96%B0%E4%B8%AA%E4%BA%BA%E4%BA%91) 的 `个人云` 部分
    - 获取 `Authorization`（仅保留 `Basic` 后的内容）
    - 该文件夹的 `目录 ID（Folder ID）` 并留存备用。

3. 上传分享文件

    在上一步的文件夹中任意上传一个文件并记下文件名。

### 4. 修改配置
复制 `config.example.yaml` 并重命名为 `config.yaml`，按照以下格式修改配置：
```yaml
139yun:
  token: "你的 Authorization"
  phone: "手机号"
  upload_dirid: "文件夹的 目录ID"
  AccountType: 1 #账号类型 1=新个人云 0=个人云 可参考Alist文档进行判断
share:
  enable: true #是否开启完成分享文件任务功能
  filename: "用来分享的文件名"
upload:
  enable: false #是否开启完成上传任务功能
```

### 5. 执行脚本
在终端中执行以下命令，运行脚本：
```bash
python ./main.py
```

## ⚠️ 注意事项
- 请勿泄露 `Authorization`，它可能被用于账户操作！

## 📄 免责声明
- 本项目仅供学习参考，请勿用于非法用途。
- 本项目及开发者与中国移动公司无任何关联。
- 本项目以 `Apache License 2.0` 协议开源。
