![caiyun-autosign](https://socialify.git.ci/unify-z/caiyun-autosign/image?description=1&language=1&name=1&owner=1&theme=Auto)
## 📖 介绍
基于 Python 的中国移动云盘（和彩云）自动签到程序

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

    参考 [AList 官方文档](https://alist.nn.ci/zh/guide/drivers/139.html#%E6%96%B0%E4%B8%AA%E4%BA%BA%E4%BA%91) 的 `新个人云` 部分
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

share:
  filename: "用来分享的文件名"
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
