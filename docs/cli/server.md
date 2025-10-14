# Server 命令参考

`faster server` 命令组用于管理开发服务器。

## faster server start

启动开发服务器。

**语法**：

```bash
faster server start
```

**配置参数**（通过 `.env` 设置）：

```bash
HOST=0.0.0.0      # 监听地址
PORT=8000         # 监听端口
DEBUG=True        # 调试模式
RELOAD=True       # 热重载
```

**启动检测逻辑**：

1. 检查项目根目录是否存在 `main.py`
2. 如果存在，优先使用用户自定义配置
3. 否则使用框架内置配置

**输出示例**：

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process [12345]
INFO:     Application startup complete.
```

**使用场景**：

- 本地开发
- 调试 API
- 查看 Swagger 文档

更多详细内容...
