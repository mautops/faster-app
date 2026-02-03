# 故障排除指南

## 常见错误

### 路由未发现
**现象：** 访问 API 返回 404

**原因：**
- APIRouter 不在模块作用域
- 文件不在 apps/ 目录
- 导入错误

**解决：**
```python
# 确保 router 在模块级别
router = APIRouter()

@router.get("/test")
async def test():
    return {"status": "ok"}
```

### 模型未注册
**现象：** 数据库操作失败

**原因：**
- 模型不继承 tortoise.Model
- 文件名不是 models.py
- 未运行迁移

**解决：**
```bash
faster db migrate --name="add_model"
faster db upgrade
```

### 配置未加载
**现象：** 使用默认配置

**原因：**
- .env 不在根目录
- 变量名错误（大小写）
- 格式错误

**解决：**
- 检查 .env 位置
- 使用大写变量名
- 字典/列表用 JSON 格式

### N+1 查询问题
**现象：** 性能差，大量查询

**原因：** 未使用 prefetch_related

**解决：**
```python
# 错误
articles = await Article.all()
for a in articles:
    print(a.author.name)  # N+1

# 正确
articles = await Article.all().prefetch_related("author")
for a in articles:
    print(a.author.name)  # OK
```

## 性能问题

### 查询慢
- 添加索引
- 使用 prefetch_related
- 限制返回数量
- 只查询需要的字段

### 启动慢
- 检查自动发现范围
- 减少中间件
- 优化导入

### 内存占用高
- 使用分页
- 避免加载大量数据
- 使用 values() 而非对象

## 调试技巧

```python
# 打印 SQL
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查配置
from faster_app.settings import configs
print(configs.DEBUG)
print(configs.DB_URL)

# 测试路由
faster_app.routes.discover.RoutesDiscover().discover()
```
