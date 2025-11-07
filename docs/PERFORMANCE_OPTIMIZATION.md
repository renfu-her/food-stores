# 性能优化指南

## 概述

本文档记录了商城系统的性能优化措施，帮助提升系统响应速度和用户体验。

---

## 已实施的优化措施

### 1. 修复 N+1 查询问题 ✅

#### 问题描述
在获取订单列表和产品列表时，对每个订单项的每个 topping 都执行单独的数据库查询，导致大量不必要的数据库请求。

#### 优化方案
- **订单 API** (`app/routes/api/orders.py`)
  - 使用 `joinedload` 和 `selectinload` 预加载关联数据
  - 批量查询所有订单项的 topping 价格，避免循环查询
  - 从 O(n*m) 次查询优化为 2-3 次查询

- **产品 API** (`app/routes/api/products.py`)
  - 使用 `selectinload` 预加载产品的 toppings 和 category
  - 批量查询所有产品的 topping 价格
  - 从 O(n*m) 次查询优化为 2-3 次查询

#### 性能提升
- **查询次数减少**：从数百次查询减少到 2-3 次
- **响应时间**：预计提升 50-80%（取决于数据量）

---

### 2. 数据库连接池配置 ✅

#### 配置内容
在 `app/config.py` 中添加了数据库连接池配置：

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,           # 连接池大小
    'pool_recycle': 3600,      # 连接回收时间（秒）
    'pool_pre_ping': True,     # 连接前检查连接是否有效
    'max_overflow': 20,        # 最大溢出连接数
}
```

#### 环境变量配置
可以通过环境变量自定义连接池参数：

```bash
DB_POOL_SIZE=10          # 连接池大小（默认：10）
DB_POOL_RECYCLE=3600     # 连接回收时间（默认：3600秒）
DB_MAX_OVERFLOW=20       # 最大溢出连接数（默认：20）
```

#### 性能提升
- **连接复用**：减少数据库连接建立和销毁的开销
- **并发处理**：支持更多并发请求
- **连接健康检查**：自动检测和回收无效连接

---

### 3. 查询优化 ✅

#### 产品列表查询优化
- 使用 `joinedload` 预加载 category，避免 N+1 查询
- 在 `app/routes/customer.py` 的店铺详情页中应用

#### 首页查询优化
- 确保查询只返回必要的字段
- 使用索引字段进行过滤（`status='active'`, `deleted_at IS NULL`）

---

## 建议的进一步优化措施

### 1. 添加数据库索引

确保以下字段有索引（如果还没有）：

```sql
-- Shop 表
CREATE INDEX idx_shop_status_deleted ON shop(status, deleted_at);
CREATE INDEX idx_shop_owner_id ON shop(owner_id);

-- Product 表
CREATE INDEX idx_product_shop_active_deleted ON product(shop_id, is_active, deleted_at);
CREATE INDEX idx_product_category ON product(category_id);

-- Order 表
CREATE INDEX idx_order_user_created ON order(user_id, created_at DESC);
CREATE INDEX idx_order_shop_status ON order(shop_id, status);
```

### 2. 使用 Redis 缓存

对于频繁访问且变化不频繁的数据，可以考虑使用 Redis 缓存：

- **首页店铺列表**：缓存 5-10 分钟
- **产品分类列表**：缓存 30 分钟
- **店铺详情**：缓存 5 分钟

### 3. 静态文件优化

- **使用 Nginx 直接提供静态文件**：避免通过 Flask 路由提供静态文件
- **启用 Gzip 压缩**：压缩 CSS、JS 文件
- **图片优化**：使用 WebP 格式（已实施），考虑 CDN

### 4. 数据库查询优化

- **分页查询**：对于列表 API，添加分页功能
- **字段选择**：只查询需要的字段，避免 `SELECT *`
- **批量操作**：使用批量插入/更新代替循环操作

### 5. 前端优化

- **懒加载**：图片和内容懒加载
- **API 请求合并**：减少 HTTP 请求次数
- **缓存策略**：使用浏览器缓存和本地存储

---

## 性能监控建议

### 1. 数据库查询监控

启用 SQLAlchemy 查询日志（开发环境）：

```bash
SQLALCHEMY_ECHO=True
```

### 2. 应用性能监控

建议使用以下工具监控应用性能：

- **Flask-Profiler**：分析请求处理时间
- **New Relic / Datadog**：生产环境监控
- **MySQL Slow Query Log**：监控慢查询

### 3. 关键指标

关注以下性能指标：

- **API 响应时间**：目标 < 200ms
- **数据库查询时间**：目标 < 50ms
- **页面加载时间**：目标 < 2s
- **并发用户数**：根据服务器配置调整

---

## 环境变量配置示例

```bash
# 数据库连接池配置
DB_POOL_SIZE=10
DB_POOL_RECYCLE=3600
DB_MAX_OVERFLOW=20

# 数据库查询日志（仅开发环境）
SQLALCHEMY_ECHO=False

# 其他配置
DEBUG=False
```

---

## 测试性能优化效果

### 1. 对比测试

在优化前后进行对比测试：

```bash
# 使用 Apache Bench 测试 API 性能
ab -n 1000 -c 10 http://your-domain.com/api/products/

# 使用 curl 测试响应时间
time curl http://your-domain.com/api/orders/
```

### 2. 数据库查询分析

使用 MySQL 的 `EXPLAIN` 分析查询计划：

```sql
EXPLAIN SELECT * FROM product WHERE shop_id = 1 AND is_active = 1;
```

---

## 注意事项

1. **连接池大小**：根据服务器配置和并发需求调整，不要设置过大
2. **缓存策略**：注意缓存失效，避免数据不一致
3. **索引维护**：定期分析索引使用情况，删除不必要的索引
4. **监控告警**：设置性能指标告警，及时发现问题

---

## 更新日志

- **2025-11-08 00:06**：实施 N+1 查询优化和数据库连接池配置

---

*最后更新：2025-11-08*

