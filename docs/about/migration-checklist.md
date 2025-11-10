# DATABASE_URL 简化调整清单

## 🎯 重构影响分析

移除向后兼容，只支持 DATABASE_URL 后，需要调整的地方：

---

## ✅ 已完成的调整

### 1. 核心代码

| 文件 | 状态 | 说明 |
|------|------|------|
| `faster_app/settings/groups/database.py` | ✅ 已更新 | 移除默认值，只支持 URL 解析 |
| `faster_app/settings/builtins/settings.py` | ✅ 已更新 | 简化初始化逻辑 |
| `examples/database_url_example.py` | ✅ 已更新 | 移除向后兼容示例 |

---

## ⚠️ 需要更新的文档

### 1. Changelog

**文件**: `docs/about/changelog.md`

**需要调整的内容**:
- ✅ v0.0.42 改为 v0.1.0（Breaking Change）
- ⚠️ 移除所有"向后兼容"的描述
- ⚠️ 移除独立环境变量的示例
- ⚠️ 添加 BREAKING CHANGE 标记

**涉及行数**: 约 20+ 处

---

### 2. 版本总结文档

**文件**: `docs/about/v0.0.42-summary.md`

**需要调整的内容**:
- ⚠️ 移除"向后兼容"章节
- ⚠️ 移除独立环境变量示例
- ⚠️ 更新为 v0.1.0
- ⚠️ 添加迁移指南

---

### 3. DATABASE_URL 文档

**文件**: `docs/features/database-url.md`

**需要调整的内容**:
```markdown
# 移除这部分（40-51行）
### 方式 3: 独立变量（向后兼容）
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=localhost
...

# 移除配置优先级中的第 4 项
4. **FASTER_DATABASE__*** - 独立环境变量

# 移除向后兼容性章节（342-344行）
- ✅ **完全向后兼容** - 独立环境变量仍然有效

# 更新迁移指南（318-330行）
改为：
## 从 v0.0.x 迁移到 v0.1.0

v0.1.0 移除了独立环境变量支持，必须使用 DATABASE_URL：

### 旧方式（v0.0.x - 不再支持）
export FASTER_DATABASE__TYPE=postgres
...

### 新方式（v0.1.0+ - 必须使用）
export DATABASE_URL=postgresql://...
```

---

### 4. Schema 文档

**文件**: `docs/features/database-schema.md`

**需要调整的内容**:
```markdown
# 移除方式 2（80-87行）
### 方式 2: 独立环境变量
export FASTER_DATABASE__TYPE=postgres
...

# 只保留方式 1: URL 查询参数
```

---

### 5. 配置分组文档

**文件**: `docs/features/config-grouping.md`

**需要调整的内容**:
```markdown
# 移除向后兼容章节（170行附近）
### 8. 向后兼容 🔄

# 移除独立环境变量示例（261-262、287-292、466-467行）
export FASTER_DATABASE__HOST=localhost
export FASTER_DATABASE__PORT=5432
```

---

### 6. 配置重构文档

**文件**: `docs/features/config-refactoring.md`

**需要调整的内容**:
```markdown
# 移除向后兼容章节（125-127行）
## 向后兼容
为了保持向后兼容...

# 移除独立环境变量示例（117-119、198、253、287行）
```

---

### 7. 环境变量前缀文档

**文件**: `docs/features/env-prefix.md`

**需要调整的内容**:
- ⚠️ 更新说明：前缀主要用于区分顶层配置
- ⚠️ 移除 `FASTER_DATABASE__*` 的独立使用示例
- ⚠️ 强调 `FASTER_DATABASE_URL` 的使用

---

## 🆕 需要新增的内容

### 1. 迁移指南文档

**新建文件**: `docs/migration/v0.0-to-v0.1.md`

```markdown
# v0.0.x → v0.1.0 迁移指南

## ⚠️ Breaking Changes

v0.1.0 移除了数据库独立环境变量支持，必须使用 DATABASE_URL。

## 迁移步骤

### 1. 识别当前配置

如果你使用的是独立环境变量：
```bash
# v0.0.x 方式（不再支持）
export FASTER_DATABASE__TYPE=postgres
export FASTER_DATABASE__HOST=localhost
export FASTER_DATABASE__PORT=5432
export FASTER_DATABASE__USER=myuser
export FASTER_DATABASE__PASSWORD=mypass
export FASTER_DATABASE__DATABASE=mydb
export FASTER_DATABASE__DB_SCHEMA=myschema  # 可选
```

### 2. 转换为 DATABASE_URL

```bash
# v0.1.0+ 方式（必须使用）
export DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydb?schema=myschema
```

### 3. 转换工具

提供一个简单的转换脚本...

## 常见问题

Q: 为什么移除向后兼容？
A: 简化代码，减少配置复杂度，符合 12-Factor App 标准。

Q: 如何快速迁移？
A: 使用我们提供的转换工具...
```

---

### 2. Changelog 更新

在 `docs/about/changelog.md` 添加 v0.1.0 章节：

```markdown
## v0.1.0 (2025-11-11) - ⚠️ Breaking Changes

??? warning "v0.1.0 - 数据库配置简化（Breaking Changes）"

    ### ⚠️ Breaking Changes
    
    - **移除独立环境变量支持**：不再支持 `FASTER_DATABASE__*` 方式
    - **必须使用 DATABASE_URL**：数据库配置只能通过 DATABASE_URL
    - **简化配置结构**：DatabaseSettings 移除默认值
    
    ### 🎉 改进
    
    - ✅ 代码更简洁
    - ✅ 配置更清晰
    - ✅ 符合 12-Factor App 标准
    - ✅ 降低维护成本
    
    ### 📖 迁移指南
    
    **v0.0.x 方式（不再支持）：**
    ```bash
    export FASTER_DATABASE__TYPE=postgres
    export FASTER_DATABASE__HOST=localhost
    export FASTER_DATABASE__PORT=5432
    ```
    
    **v0.1.0+ 方式（必须使用）：**
    ```bash
    export DATABASE_URL=postgresql://user:pass@localhost:5432/db
    ```
    
    详细迁移指南：[v0.0.x → v0.1.0 迁移](../migration/v0.0-to-v0.1.md)
```

---

## 📋 执行计划

### 优先级 1（立即执行）

1. ✅ 更新核心代码（已完成）
2. ⚠️ 创建迁移指南文档
3. ⚠️ 更新 Changelog（添加 v0.1.0）
4. ⚠️ 更新版本号到 v0.1.0

### 优先级 2（批量更新）

5. ⚠️ 更新所有特性文档（移除向后兼容描述）
6. ⚠️ 更新示例代码注释
7. ⚠️ 检查并更新所有配置示例

### 优先级 3（完善）

8. ⚠️ 添加自动化转换脚本
9. ⚠️ 更新测试用例
10. ⚠️ 发布公告

---

## 🔍 检查清单

### 代码
- [x] `faster_app/settings/groups/database.py`
- [x] `faster_app/settings/builtins/settings.py`
- [x] `examples/database_url_example.py`

### 文档
- [ ] `docs/about/changelog.md`
- [ ] `docs/about/v0.0.42-summary.md` → 重命名为 `v0.1.0-summary.md`
- [ ] `docs/features/database-url.md`
- [ ] `docs/features/database-schema.md`
- [ ] `docs/features/config-grouping.md`
- [ ] `docs/features/config-refactoring.md`
- [ ] `docs/features/env-prefix.md`
- [ ] 新建 `docs/migration/v0.0-to-v0.1.md`

### 配置
- [ ] `pyproject.toml` - 更新版本号
- [ ] README.md - 检查是否有相关说明
- [ ] .env.example - 如果存在，需要更新

---

## 📊 统计

| 类别 | 数量 | 状态 |
|------|------|------|
| 代码文件 | 3 | ✅ 已完成 |
| 文档文件 | 7-8 | ⚠️ 待更新 |
| 新建文件 | 1 | ⚠️ 待创建 |
| 影响行数 | ~150+ | ⚠️ 待处理 |

---

## 💡 建议

1. **渐进式发布**
   - 先发布 RC 版本让用户测试
   - 收集反馈后正式发布 v0.1.0
   
2. **清晰的沟通**
   - 在 GitHub Release 中明确标注 Breaking Changes
   - 提供详细的迁移指南
   - 在社交媒体/文档首页突出提示
   
3. **辅助工具**
   - 提供配置转换脚本
   - 提供配置验证工具
   
4. **文档优先**
   - 先完善迁移指南
   - 再批量更新其他文档

---

## ✅ 总结

**已完成**:
- ✅ 核心代码重构（3 个文件）
- ✅ 示例代码更新

**待完成**:
- ⚠️ 文档更新（7-8 个文件）
- ⚠️ 迁移指南创建
- ⚠️ 版本号更新
- ⚠️ Changelog 更新

**预计工作量**: 1-2 小时

**建议时间安排**:
1. 先创建迁移指南（30分钟）
2. 再批量更新文档（60分钟）
3. 最后更新版本和 Changelog（30分钟）

