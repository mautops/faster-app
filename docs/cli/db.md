# DB 命令参考

`faster db` 命令组用于数据库管理，基于 Aerich 实现。

## 命令列表

| 命令        | 说明           | 使用频率   |
| ----------- | -------------- | ---------- |
| `init`      | 初始化迁移配置 | ⭐⭐⭐⭐⭐ |
| `init_db`   | 初始化数据库   | ⭐⭐⭐⭐⭐ |
| `migrate`   | 生成迁移文件   | ⭐⭐⭐⭐⭐ |
| `upgrade`   | 执行迁移       | ⭐⭐⭐⭐⭐ |
| `downgrade` | 回滚迁移       | ⭐⭐⭐     |
| `history`   | 查看历史       | ⭐⭐⭐     |
| `heads`     | 查看待应用迁移 | ⭐⭐⭐     |
| `dev_clean` | 清理开发数据   | ⭐⭐       |

## faster db init

初始化数据库迁移配置。

**语法**：

```bash
faster db init
```

**功能说明**：

- 创建 `migrations/` 目录
- 初始化 Aerich 配置
- 准备数据库迁移环境

**使用场景**：

- 项目首次设置
- 重置迁移系统（配合 `dev_clean`）

## faster db migrate

生成数据库迁移文件。

**语法**：

```bash
# 自动生成
faster db migrate

# 指定名称
faster db migrate --name="add_user_table"

# 生成空迁移
faster db migrate --empty
```

**参数说明**：

- `--name`: 迁移文件名称（可选）
- `--empty`: 生成空迁移文件

更多详细内容...
