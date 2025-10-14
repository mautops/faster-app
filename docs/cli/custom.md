# 自定义命令

本页面介绍如何创建和使用自定义命令。

## 创建自定义命令

```python
# apps/users/commands.py
from faster_app.commands.base import BaseCommand
from .models import User

class UserCommand(BaseCommand):
    """用户管理命令"""

    async def create_admin(self, username: str, email: str):
        """创建管理员账号"""
        user = await User.create(
            username=username,
            email=email,
            is_staff=True
        )
        print(f"✅ 管理员 {username} 创建成功")

    async def count(self):
        """统计用户数量"""
        count = await User.all().count()
        print(f"总用户数: {count}")
```

## 使用自定义命令

```bash
faster user create_admin --username=admin --email=admin@example.com
faster user count
```

## 命名规则

类名自动转换为命令组名：

| 类名                 | 命令组         |
| -------------------- | -------------- |
| `UserCommand`        | `user`         |
| `ArticleCommand`     | `article`      |
| `UserProfileCommand` | `user_profile` |

更多详细内容...
