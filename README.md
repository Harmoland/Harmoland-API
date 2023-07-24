# Harmoland API

桦木原服务器玩家管理 API

## 已实现功能

### 玩家相关（QQ群成员）

- 新增/修改一个玩家的信息
- 获取某个玩家的信息
- 获取所有玩家列表
- 获取所有被 Ban 的 QQ
- Ban 一个玩家
- 解 Ban 一个玩家

### 白名单相关

- 获取某个某个 UUID 的信息
- 获取白名单中的所有 UUID
- 添加一个新的白名单
- 删除已有的白名单
- 通过玩家QQ删除白名单

### 封禁相关

- 获取所有被 Ban 的 UUID
- Ban 一个 UUID
- 解 Ban 一个 UUID

### 其他

- Oauth2 登录
- Oauth2 新增用户

## 部署

1. 确保你的系统内已安装的 Python 版本大于或等于 `3.10`
2. 安装 pipx
   - Ubuntu / Debian: `sudo apt install pipx`
   - 其他 Linux 或 macOS：先搜索系统包管理器内是否有 `pipx`，如没有则使用
     `python3 -m pip install -U pipx` 或 `python3.10/3.11 -m pip install -U pipx` 安装 `pipx`
     > 在较新的 Linux 系统上，可能会阻止你在系统自带的 Python 中安装新的包，也不建议在系统自带的
     > Python 上安装任何包，建议使用 `make altinstall` 或其他方式从源码编译安装不会覆盖系统自带
     > Python 的独立 Python
   - Windows: `python -m pip install -U pipx`
3. 使用 `pipx install pdm` 安装 pdm
   > 在某些 Linux 系统上，还可能需要将 `$HOME/.local/bin` 添加至环境变量
4. Clone 本仓库并进入本项目目录
5. 使用 `pdm install` 安装依赖
6. 使用 `pdm run main.py` 启动 API
7. 浏览器打开 <http://127.0.0.1:8000/docs> 查看 API 文档并在线调试 API

## 疑难解答

### 启动时提示 `ConnectionRefusedError: [WinError 1225] 远程计算机拒绝网络连接`

API 启动时会尝试通过 RCON 连接服务器，你需要关闭 API 并开启一个 Minecraft 服务器再尝试

### 如何修改 API 的监听地址和端口或者 RCON 连接的地址和端口

在 `main.py` 内修改

```python
launart.add_service(UvicornService(host="127.0.0.1", port=8000))
launart.add_service(RconService("127.0.0.1", 25575, passwd="111funnyguy"))
```

### 如何退出 API

`Ctrl + C`
