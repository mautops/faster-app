# 开发环境

本页面介绍如何设置 Faster APP 的开发环境。

## 克隆仓库

```bash
git clone https://github.com/mautops/faster-app.git
cd faster-app
```

## 安装依赖

```bash
# 使用 uv
uv sync

# 安装开发依赖
uv sync --dev
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 查看覆盖率
pytest --cov=faster_app
```

更多详细内容...
