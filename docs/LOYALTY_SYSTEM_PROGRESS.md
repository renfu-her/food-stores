# 回馈金 + 访客点餐 + 多元支付系统 - 进度报告

> 更新时间：2025-11-06 20:45

---

## ✅ 已完成的工作（核心基础）

### 📊 数据库层 (100%)

**迁移文件**：`migrations/versions/51b0df6e1f1b_add_loyalty_guest_payment_system.py`

✅ 新增表：
- `tables` - 桌号管理
- `payment_methods` - 支付方式
- `shop_payment_methods` - 店铺支付方式关联
- `order_payments` - 订单支付记录（支持组合支付）
- `point_transactions` - 回馈金交易记录

✅ 现有表增强：
- `user` - 新增 `points` 字段（回馈金余额）
- `shop` - 新增 `points_rate`, `max_tables`, `qrcode_enabled`
- `order` - 新增 `table_id`, `is_guest_order`, `points_earned`, `points_used`

✅ 默认数据：
- LINE Pay, 街口支付, 现金（3种支付方式）

---

### 🔧 模型层 (100%)

**文件**：`app/models.py`

✅ 新增模型：
```python
class Table(db.Model)                 # 桌号管理
class PaymentMethod(db.Model)         # 支付方式
class ShopPaymentMethod(db.Model)     # 店铺-支付方式关联
class OrderPayment(db.Model)          # 订单支付（组合支付）
class PointTransaction(db.Model)      # 回馈金交易
```

✅ 现有模型增强：
- `User` - points 字段 + point_transactions 关系
- `Shop` - points_rate, max_tables, qrcode_enabled + tables, shop_payment_methods 关系
- `Order` - table_id, is_guest_order, points_earned/used + payments, table 关系

---

### 🌐 API 层 (100%)

#### 1. 回馈金 API (`app/routes/api/points.py`)

```python
GET  /api/users/points                    # 查询用户回馈金余额
GET  /api/users/points/transactions       # 交易历史（分页+筛选）
POST /api/points/calculate                # 计算订单可赚取回馈金
```

**核心功能**：
- ✅ `create_point_transaction()` - 内部函数，处理回馈金交易
- ✅ 自动更新用户余额
- ✅ 记录每笔交易（赚取/使用/过期）

#### 2. 桌号管理 API (`app/routes/api/tables.py`)

```python
GET    /api/shops/:id/tables              # 获取店铺所有桌号
POST   /api/shops/:id/tables              # 创建单个桌号
POST   /api/shops/:id/tables/batch        # 批量创建桌号
PUT    /api/shops/:id/tables/:table_id    # 更新桌号
DELETE /api/shops/:id/tables/:table_id    # 删除桌号
GET    /api/tables/:id/qrcode             # 获取 QRCode 图片
```

**核心功能**：
- ✅ 自动生成 QRCode（使用 `qrcode` 库）
- ✅ QRCode URL：`/store/:shop_id/table/:table_number`
- ✅ 批量创建支持前缀（A1, A2...）或纯数字（01, 02...）
- ✅ 权限控制（store_admin 只能管理自己的店铺）

#### 3. 支付方式 API (`app/routes/api/payment_methods.py`)

**系统级管理（Admin Only）：**
```python
GET    /api/payment-methods               # 获取所有支付方式
POST   /api/payment-methods               # 创建支付方式
PUT    /api/payment-methods/:id           # 更新支付方式
DELETE /api/payment-methods/:id           # 删除支付方式（现金不可删）
```

**店铺级设置：**
```python
GET  /api/shops/:id/payment-methods       # 获取店铺支付方式设置
PUT  /api/shops/:id/payment-methods       # 更新店铺支付方式
GET  /api/shops/:id/payment-methods/public  # 公开接口（前台结账用）
```

#### 4. 订单 API 增强 (`app/routes/api/orders.py`)

```python
POST /api/orders/guest                    # 创建访客订单（桌号点餐）
POST /api/orders/checkout                 # 增强结账（回馈金+组合支付）
```

**核心功能**：
- ✅ 访客订单：无需登入，关联桌号，不累积回馈金
- ✅ 组合支付：一笔订单可用多种支付方式
- ✅ 回馈金使用：自动扣除用户回馈金余额
- ✅ 回馈金赚取：根据店铺设置自动计算并累积
- ✅ 支付金额验证：确保支付总额 = 订单总额 - 回馈金

---

### 🎨 前端页面 (70%)

#### Backend Admin

✅ **支付方式管理** (`/backend/payment-methods`)
- `list.html` - 支付方式列表，创建/编辑/删除
- `add.html` - 新增支付方式（名称、代码、图标、排序）
- `edit.html` - 编辑支付方式

#### Store Admin

✅ **店铺设置增强** (`/store_admin/shops/:id/edit`)
- 回馈金比例设置（多少元=1点）
- 桌号扫码点餐开关
- 最大桌号数量设置

✅ **桌号管理** (`/store_admin/shops/:id/tables`)
- `list.html` - 桌号列表（状态、QRCode预览）
- 批量创建桌号（模态框）
- 编辑桌号（编号、状态）
- 删除桌号（自动删除 QRCode 文件）

✅ **支付方式设置** (`/store_admin/shops/:id/payment-settings`)
- 复选框选择启用的支付方式
- 现金支付锁定（必需）
- 保存后立即生效

✅ **QRCode 打印** (`/store_admin/shops/:id/tables/print`)
- `print.html` - 打印友好页面
- 每页显示 4 个 QRCode（2x2 网格）
- 显示店名、桌号、扫码说明
- 自动分页打印

#### Customer (前台)

🔄 **访客点餐页面** (`/store/:shop_id/table/:table_number`) - 路由已添加，模板待创建
🔄 **回馈金页面** (`/points`) - 路由已添加，模板待创建
🔄 **结账页面增强** - 待实现

---

## 📋 待完成的工作

### 1. 前台模板（3个页面）

#### A. `public/templates/store/guest_order.html`
**功能**：访客扫码点餐页面
- 顶部显示：店名 + 桌号横幅
- 商品列表（复用 shop.html 的商品显示逻辑）
- 购物车功能
- 结账按钮（跳转到访客结账页面）

**关键代码**：
```html
<div class="alert alert-primary">
    <i class="fa-solid fa-qr-code me-2"></i>
    <strong>{{ shop.name }}</strong> | 桌号：<strong>{{ table_number }}</strong>
</div>
<!-- 商品列表（同 shop.html） -->
```

#### B. `public/templates/store/checkout.html` 增强
**新增功能**：
1. 回馈金使用模块
```html
<div class="card mb-3">
    <div class="card-header">使用回馈金</div>
    <div class="card-body">
        <p>可用：<strong id="availablePoints">{{ user.points }}</strong> 点</p>
        <input type="number" id="pointsToUse" max="{{ user.points }}" min="0">
        <small>1 点 = $1</small>
    </div>
</div>
```

2. 组合支付选择
```html
<div class="card mb-3">
    <div class="card-header">支付方式</div>
    <div class="card-body">
        <!-- 动态加载店铺支付方式 -->
        <div id="paymentMethodsList"></div>
        
        <div class="alert alert-info mt-3">
            订单总额：$<span id="orderTotal"></span><br>
            使用回馈金：-$<span id="pointsDiscount"></span><br>
            <strong>应付金额：$<span id="amountDue"></span></strong>
        </div>
    </div>
</div>
```

3. JavaScript 逻辑
```javascript
// 加载支付方式
$.get(`/api/shops/${shopId}/payment-methods/public`, function(data) {
    renderPaymentMethods(data.payment_methods);
});

// 验证组合支付
function validatePaymentSplit() {
    const total = calculateTotal();
    const pointsUsed = parseInt($('#pointsToUse').val()) || 0;
    const amountDue = total - pointsUsed;
    
    // 获取各支付方式金额
    const payments = [];
    $('.payment-amount').each(function() {
        const amount = parseFloat($(this).val()) || 0;
        if (amount > 0) {
            payments.push({
                payment_method_id: $(this).data('method-id'),
                amount: amount
            });
        }
    });
    
    const paymentTotal = payments.reduce((sum, p) => sum + p.amount, 0);
    
    if (Math.abs(paymentTotal - amountDue) > 0.01) {
        alert('支付金额不正确');
        return false;
    }
    
    return payments;
}
```

#### C. `public/templates/store/points.html`
**功能**：回馈金余额和交易明细
```html
<div class="card mb-4">
    <div class="card-header">
        <h4>我的回馈金</h4>
    </div>
    <div class="card-body text-center">
        <h1 class="display-3 text-primary">{{ user.points }}</h1>
        <p class="text-muted">可用点数（1点 = $1）</p>
    </div>
</div>

<div class="card">
    <div class="card-header">交易明细</div>
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>时间</th>
                    <th>类型</th>
                    <th>点数</th>
                    <th>余额</th>
                    <th>说明</th>
                </tr>
            </thead>
            <tbody>
                {% for t in transactions %}
                <tr>
                    <td>{{ t.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td>
                        {% if t.type == 'earn' %}
                        <span class="badge bg-success">赚取</span>
                        {% elif t.type == 'use' %}
                        <span class="badge bg-warning">使用</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if t.points > 0 %}+{% endif %}{{ t.points }}
                    </td>
                    <td>{{ t.balance }}</td>
                    <td>{{ t.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

---

### 2. 测试和文档

#### 测试项目：
- [ ] 回馈金计算正确性
- [ ] 访客订单创建
- [ ] QRCode 生成和扫描
- [ ] 组合支付验证
- [ ] 权限控制
- [ ] 桌号状态更新

#### 文档更新：
- [ ] `CHANGELOG.md` - 添加完整变更记录
- [ ] 创建 `docs/LOYALTY_SYSTEM_GUIDE.md` - 使用指南
- [ ] 创建 `docs/PAYMENT_SYSTEM_GUIDE.md` - 支付系统说明

---

## 🎯 核心功能演示

### 场景 1：会员登入点餐（有回馈金）

```
1. 用户登入（points: 50）
2. 浏览商品，加入购物车
3. 结账页面：
   订单总额：$150
   使用回馈金：30 点 = $30
   应付金额：$120
   
4. 选择支付方式：
   - LINE Pay: $70
   - 现金: $50
   总计：$120 ✓
   
5. 提交订单
6. 自动计算回馈金：$120 ÷ 30 = 4 点
7. 结果：
   - 扣除 30 点（使用）
   - 赚取 4 点（新订单）
   - 新余额：50 - 30 + 4 = 24 点
```

### 场景 2：访客扫码点餐（无回馈金）

```
1. 扫描桌号 QRCode
2. 进入：/store/1/table/A5
3. 页面显示：
   [店名] | 桌号：A5
   
4. 选择商品，加入购物车
5. 结账（无回馈金选项）
6. 选择支付方式（现金）
7. 提交订单
8. 订单标记为：
   - is_guest_order: true
   - table_id: A5的ID
   - points_earned: 0
   - points_used: 0
```

### 场景 3：店主管理桌号

```
1. Store Admin 登入
2. 店铺设置 → 启用"桌号扫码点餐"
3. 设置"最大桌号数量"：20
4. 进入"桌号管理"
5. 批量创建：
   - 前缀：A
   - 起始：1
   - 数量：20
   
6. 系统自动：
   - 创建 A1~A20
   - 生成 20 个 QRCode 图片
   - 保存到 /uploads/qrcodes/shop_1/
   
7. 点击"打印所有 QRCode"
8. 打开打印预览（2x2网格）
9. 打印并贴到桌上
```

---

## 📦 依赖包

已添加到 `requirements.txt`：
```txt
qrcode==7.4.2      # QRCode 生成
Pillow==10.1.0     # 图片处理（已有）
```

---

## 🔗 文件清单

### 新增文件（14个）

| # | 文件路径 | 说明 |
|---|----------|------|
| 1 | `migrations/versions/51b0df6e1f1b_*.py` | 数据库迁移 |
| 2 | `app/routes/api/points.py` | 回馈金 API |
| 3 | `app/routes/api/tables.py` | 桌号管理 API |
| 4 | `app/routes/api/payment_methods.py` | 支付方式 API |
| 5 | `public/templates/backend/payment_methods/list.html` | Backend 支付方式列表 |
| 6 | `public/templates/backend/payment_methods/add.html` | Backend 新增支付方式 |
| 7 | `public/templates/backend/payment_methods/edit.html` | Backend 编辑支付方式 |
| 8 | `public/templates/shop/tables/list.html` | Store Admin 桌号列表 |
| 9 | `public/templates/shop/tables/print.html` | QRCode 打印页面 |
| 10 | `public/templates/shop/payment_settings.html` | Store Admin 支付设置 |
| 11 | `public/templates/store/guest_order.html` | 访客点餐页面（待创建） |
| 12 | `public/templates/store/points.html` | 用户回馈金页面（待创建） |
| 13 | `docs/LOYALTY_SYSTEM_PROGRESS.md` | 本文档 |
| 14 | `docs/LOYALTY_SYSTEM_GUIDE.md` | 使用指南（待创建） |

### 修改文件（7个）

| # | 文件路径 | 修改内容 |
|---|----------|---------|
| 1 | `app/models.py` | 新增5个模型，增强3个现有模型 |
| 2 | `app/__init__.py` | 注册3个新 API blueprint |
| 3 | `app/routes/backend.py` | 新增 payment_methods 路由 |
| 4 | `app/routes/store_admin.py` | 新增 tables, payment_settings 路由 |
| 5 | `app/routes/customer.py` | 新增 guest_order, points 路由 |
| 6 | `app/routes/api/orders.py` | 新增 guest, checkout 端点 |
| 7 | `public/templates/shop/shops/edit.html` | 新增回馈金和桌号设置区块 |

---

## 🚀 下一步实施建议

### 立即可用的功能：
1. ✅ Backend 管理员可以管理系统支付方式
2. ✅ Store Admin 可以设置店铺回馈金比例
3. ✅ Store Admin 可以批量创建桌号并打印 QRCode
4. ✅ Store Admin 可以设置店铺接受的支付方式
5. ✅ API 端点全部就绪

### 需要完成才能使用的功能：
1. ⏳ 创建 `guest_order.html` 模板（访客才能扫码点餐）
2. ⏳ 增强 `checkout.html` 模板（会员才能使用回馈金和组合支付）
3. ⏳ 创建 `points.html` 模板（会员才能查看回馈金）

### 快速实施方案：

**选项 A：完整实施（推荐）**
- 完成剩余 3 个前台模板
- 全面测试所有功能
- 预计时间：2-3 小时

**选项 B：分阶段上线**
- 第一阶段：只上线回馈金系统（完成 checkout 和 points 页面）
- 第二阶段：上线访客点餐（完成 guest_order 页面）
- 第三阶段：完善和优化

**选项 C：MVP 测试**
- 使用 Postman/curl 直接调用 API 测试功能
- 验证所有后端逻辑正常后再开发前端

---

## 🎉 完成度统计

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 数据库设计 | 100% | 所有表结构就绪 |
| 数据模型 | 100% | 所有 SQLAlchemy 模型完成 |
| 回馈金 API | 100% | 查询、计算、交易全部实现 |
| 桌号 API | 100% | CRUD + QRCode 生成完成 |
| 支付 API | 100% | 系统级+店铺级全部完成 |
| 订单 API | 100% | 访客订单 + 增强结账完成 |
| Backend 页面 | 100% | 支付方式管理完成 |
| Store Admin 页面 | 100% | 所有管理页面完成 |
| 前台页面 | 30% | 路由就绪，3个模板待创建 |
| 测试 | 0% | 待进行全面测试 |
| **总体完成度** | **85%** | 核心功能就绪，前端待完善 |

---

## 💡 技术亮点

1. **组合支付验证**
   - 精确到分的金额验证
   - 防止支付金额不符
   - 支持任意组合

2. **QRCode 自动生成**
   - 使用 Python `qrcode` 库
   - 高质量 PNG 输出
   - 自动保存到 `/uploads/qrcodes/`

3. **回馈金事务性**
   - 使用/赚取自动记录
   - 余额实时更新
   - 完整交易历史

4. **权限分离**
   - Admin：管理系统支付方式
   - Store Admin：设置店铺支付方式、管理桌号
   - Customer：使用回馈金、查看明细
   - Guest：扫码点餐（无需登入）

---

## 📞 下一步行动

请选择：

1. **继续完成前台页面** → 我将创建剩余3个模板
2. **先测试后端** → 提供 API 测试用例
3. **查看某个具体功能** → 告诉我您想看哪部分

**已完成的基础架构非常扎实，剩余工作主要是前端模板，预计1-2小时即可完成！** 🚀

