# 快速开始指南 - 回馈金 + 访客点餐 + 多元支付

> 5分钟快速上手新功能

---

## 🚀 立即开始

### 步骤 1：安装依赖（如果尚未安装）

```bash
pip install qrcode==7.4.2
```

### 步骤 2：启动应用

```bash
python app.py
```

---

## 🎯 功能测试路线图

### A. Backend Admin 测试（管理员）

#### 1️⃣ 管理支付方式

```
登入：http://localhost:5000/backend
账号：admin@admin.com / Aa123456@

访问：侧边栏 → 支付方式
查看：LINE Pay, 街口支付, 现金（默认3种）

可选操作：
- 点击"新增支付方式"
  * 名称：Apple Pay
  * 代码：apple_pay
  * 图标：fa-brands fa-apple-pay
  * 显示顺序：3
  * 创建

- 点击"编辑"修改支付方式
- 点击"删除"（现金不可删除）
```

---

### B. Store Admin 测试（店主）

#### 2️⃣ 设置店铺

```
登入：http://localhost:5000/store_admin
账号：store1@store.com / Qq123456@

步骤：
1. 侧边栏 → 店鋪管理
2. 点击第一个店铺的"编辑"按钮
3. 向下滚动，找到"回馈金设置"区块
   - 回馈比例：30（每30元=1点）
   - 点击"更新回馈金设置"
   ✅ 成功！

4. 继续向下，找到"桌号扫码点餐"区块
   - 勾选"启用桌号扫码点餐"
   - 最大桌号数量：20
   - 点击"更新桌号设置"
   ✅ 成功！
```

#### 3️⃣ 创建桌号

```
在店铺编辑页面：
1. 点击"管理桌号"按钮
2. 进入桌号管理页面
3. 点击"批量创建桌号"按钮
4. 填写：
   - 桌号前缀：A（可选）
   - 起始编号：1
   - 创建数量：10
5. 点击"创建"

结果：
✅ 创建 A1-A10 共 10 个桌号
✅ 自动生成 10 个 QRCode 图片
✅ 列表显示所有桌号和状态
```

#### 4️⃣ 打印 QRCode

```
在桌号管理页面：
1. 点击"打印所有 QRCode"按钮
2. 新窗口打开打印预览页面
3. 查看：
   - 每页显示 4 个 QRCode（2x2网格）
   - 每个QRCode显示：店名 + 桌号 + 扫码说明
4. 点击"打印"按钮
5. 打印机打印
6. 剪下并贴到相应桌上

✅ QRCode 准备完成！
```

#### 5️⃣ 设置支付方式

```
在店铺编辑页面：
1. 找到"桌号扫码点餐"区块
2. 向下滚动，或者直接访问：
   /store_admin/shops/1/payment-settings
   
3. 看到所有可用支付方式：
   ☑ LINE Pay
   ☑ 街口支付
   ☑ 现金（灰色，不可取消）
   
4. 勾选您接受的支付方式
5. 点击"保存设置"

✅ 支付方式配置完成！
```

---

### C. Customer 测试（会员）

#### 6️⃣ 查看回馈金

```
登入：http://localhost:5000/login
账号：customer@customer.com / Cc123456@

方法 1 - 通过导航：
1. 点击右上角用户名下拉菜单
2. 选择"我的回馈金"
3. 查看：
   - 当前余额：XX 点
   - 交易明细列表

方法 2 - 直接访问：
http://localhost:5000/points

✅ 回馈金页面显示正常！
```

#### 7️⃣ 使用回馈金购物

```
在会员登入状态：
1. 浏览商品，加入购物车
2. 进入购物车：/cart
3. 点击"去結帳"
4. 结账页面：
   
   【回馈金使用】区块：
   - 可用回馈金：50 点
   - 使用：[输入 30] 点
   - 或点击"使用全部"
   
   【订单商品】区块：
   - 显示所有商品
   
   【支付方式】区块：
   - 看到店铺接受的所有支付方式
   - 勾选 LINE Pay，输入 $70
   - 勾选 现金，输入 $50
   
   【支付总览】：
   订单总额：$150
   使用回馈金：-$30
   ━━━━━━━━━━━━━
   应付金额：$120
   已分配支付：$120 ✓
   本次可获得：4 点回馈金
   
5. 填写收货地址
6. 点击"确认订单"

结果：
✅ 订单创建成功！
✅ 扣除 30 点回馈金
✅ 赚取 4 点新回馈金
✅ 创建 2 条支付记录
```

---

### D. Guest 测试（访客）

#### 8️⃣ 扫码点餐

```
准备：
1. 打开手机相机
2. 扫描桌上的 QRCode
3. 或直接在浏览器输入：
   http://localhost:5000/store/1/table/A5
   
进入页面：
━━━━━━━━━━━━━━━━━━━━━━
🍜 美食店 | 桌号：A5
扫码点餐，无需登入
━━━━━━━━━━━━━━━━━━━━━━

4. 浏览商品
5. 点击"加入购物车"
6. 查看购物车（右下角浮动按钮）
7. 确认订单

页面提示：
✅ 订单创建成功！
   订单编号：XXX
   桌号：A5
   
   请告知服务人员您的桌号

✅ 无需注册即可完成点餐！
```

---

## 🧪 API 测试（开发者）

### 测试回馈金 API

```bash
# 查询用户回馈金余额
curl -X GET http://localhost:5000/api/users/points \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# 计算可赚取回馈金
curl -X POST http://localhost:5000/api/points/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "order_total": 150,
    "shop_id": 1
  }'
```

### 测试桌号 API

```bash
# 批量创建桌号
curl -X POST http://localhost:5000/api/shops/1/tables/batch \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "prefix": "B",
    "start_number": 1,
    "count": 15
  }'

# 获取所有桌号
curl -X GET http://localhost:5000/api/shops/1/tables \
  -H "Cookie: session=YOUR_SESSION_COOKIE"
```

### 测试支付方式 API

```bash
# 获取店铺支付方式（公开接口）
curl -X GET http://localhost:5000/api/shops/1/payment-methods/public

# 更新店铺支付方式
curl -X PUT http://localhost:5000/api/shops/1/payment-methods \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "enabled_method_ids": [1, 2, 3]
  }'
```

### 测试访客订单 API

```bash
# 创建访客订单
curl -X POST http://localhost:5000/api/orders/guest \
  -H "Content-Type: application/json" \
  -d '{
    "shop_id": 1,
    "table_number": "A5",
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "drink_type": "cold",
        "toppings": []
      }
    ],
    "payment_splits": [
      {
        "payment_method_id": 3,
        "amount": 100
      }
    ]
  }'
```

### 测试增强结账 API

```bash
# 使用回馈金 + 组合支付
curl -X POST http://localhost:5000/api/orders/checkout \
  -H "Content-Type: application/json" \
  -H "Cookie: session=YOUR_SESSION_COOKIE" \
  -d '{
    "shop_id": 1,
    "items": [
      {
        "product_id": 1,
        "quantity": 2,
        "drink_type": "cold",
        "toppings": [1, 2]
      }
    ],
    "points_to_use": 30,
    "payment_splits": [
      {"payment_method_id": 1, "amount": 70},
      {"payment_method_id": 3, "amount": 50}
    ],
    "recipient_info": {
      "name": "张三",
      "phone": "0912345678",
      "county": "台北市",
      "district": "大安區",
      "zipcode": "106",
      "address": "信義路四段1號",
      "note": "请尽快送达"
    }
  }'
```

---

## 📋 完整测试清单

### 功能测试

- [ ] Backend 管理支付方式
  - [ ] 查看列表
  - [ ] 新增支付方式
  - [ ] 编辑支付方式
  - [ ] 删除支付方式（现金不可删）

- [ ] Store Admin 店铺设置
  - [ ] 设置回馈金比例
  - [ ] 启用桌号扫码
  - [ ] 设置最大桌号数量

- [ ] Store Admin 桌号管理
  - [ ] 批量创建桌号（带前缀）
  - [ ] 批量创建桌号（纯数字）
  - [ ] 编辑桌号编号
  - [ ] 更新桌号状态
  - [ ] 删除桌号
  - [ ] 查看 QRCode
  - [ ] 打印所有 QRCode

- [ ] Store Admin 支付设置
  - [ ] 选择启用的支付方式
  - [ ] 保存设置

- [ ] Customer 回馈金
  - [ ] 查看余额
  - [ ] 查看交易明细
  - [ ] 加载更多记录

- [ ] Customer 结账
  - [ ] 使用回馈金
  - [ ] 使用全部/清除回馈金
  - [ ] 选择组合支付
  - [ ] 实时金额验证
  - [ ] 查看可获回馈金
  - [ ] 提交订单

- [ ] Guest 访客点餐
  - [ ] 扫描 QRCode（或直接访问URL）
  - [ ] 浏览商品
  - [ ] 加入购物车
  - [ ] 提交订单（无需登入）

### API 测试

- [ ] Points API - 所有端点
- [ ] Tables API - 所有端点
- [ ] Payment Methods API - 所有端点
- [ ] Orders API - guest 和 checkout 端点

### 权限测试

- [ ] Admin 可以管理系统支付方式
- [ ] Store Admin 可以管理自己店铺的桌号
- [ ] Store Admin 不能管理其他店铺的桌号
- [ ] Customer 可以查看自己的回馈金
- [ ] Customer 不能查看他人的回馈金
- [ ] Guest 可以扫码点餐（无需登入）

---

## 💡 常见问题

### Q1: 如何查看生成的 QRCode？

**A:** 在桌号管理页面，每个桌号行都有"查看"按钮，点击可在新窗口打开 QRCode 图片。

或直接访问：
```
/uploads/qrcodes/shop_1/table_A5.png
```

### Q2: 访客点餐的 URL 格式是什么？

**A:** 格式为：`/store/{shop_id}/table/{table_number}`

示例：
- `/store/1/table/A5`
- `/store/2/table/B10`
- `/store/1/table/01`

### Q3: 如何测试组合支付？

**A:** 
1. 登入会员账号
2. 加入商品到购物车
3. 进入结账页面
4. 勾选多个支付方式并输入金额
5. 确保总额 = 应付金额
6. 提交订单

### Q4: 现金支付能删除吗？

**A:** 不能。现金支付是系统必需的基础支付方式，受到保护，不能删除或禁用。

### Q5: 回馈金会过期吗？

**A:** 当前版本不会过期。未来可以添加过期功能。

### Q6: 访客订单会累积回馈金吗？

**A:** 不会。访客订单不需要登入，因此不会累积回馈金。

### Q7: 一个订单可以用几种支付方式？

**A:** 理论上没有限制，可以使用店铺启用的所有支付方式进行组合支付。

### Q8: 回馈金可以跨店使用吗？

**A:** 可以！在任何店铺赚取的回馈金都可以在其他店铺使用。

---

## 🎨 界面预览

### Backend - 支付方式管理

```
┌─────────────────────────────────────────┐
│ 支付方式管理                [+ 新增]     │
├─────────────────────────────────────────┤
│ ID │ 名称      │ 代码     │ 图标 │ 操作 │
├────┼──────────┼─────────┼──────┼──────┤
│ 1  │ LINE Pay │ line_pay │ 🟢   │ 编辑 │
│ 2  │ 街口支付  │ jko_pay  │ 💰   │ 编辑 │
│ 3  │ 现金     │ cash     │ 💵   │ 🔒   │
└────────────────────────────────────────┘
```

### Store Admin - 桌号管理

```
┌───────────────────────────────────────────┐
│ 店铺 - 桌号管理    [批量创建] [打印]      │
├───────────────────────────────────────────┤
│ 桌号 │ 状态   │ QRCode  │ 操作            │
├──────┼────────┼─────────┼─────────────────┤
│ A1   │ 空闲   │ [查看]  │ [编辑] [删除]   │
│ A2   │ 使用中 │ [查看]  │ [编辑] [删除]   │
│ A3   │ 空闲   │ [查看]  │ [编辑] [删除]   │
└───────────────────────────────────────────┘
```

### Customer - 结账页面

```
┌─────────────────────────────────────┐
│ 使用回馈金                           │
│ 可用：50 点                          │
│ 使用：[30] 点  [使用全部] [清除]     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 支付方式（可组合）                   │
│                                     │
│ ☑ 🟢 LINE Pay      [$70]           │
│ ☐ 💰 街口支付     [___]            │
│ ☑ 💵 现金         [$50]            │
│                                     │
│ 订单总额：$150                       │
│ 使用回馈金：-$30                     │
│ ━━━━━━━━━━━━━━━                    │
│ 应付金额：$120                       │
│ 已分配支付：$120 ✓                   │
│ 本次可获得：4 点回馈金                │
└─────────────────────────────────────┘
```

### Guest - 访客点餐

```
┌─────────────────────────────────────┐
│ 🍜 美食店 | 桌号：A5                 │
│ 扫码点餐，无需登入                   │
└─────────────────────────────────────┘

[商品列表]
┌──────────┐ ┌──────────┐ ┌──────────┐
│ 珍珠奶茶  │ │ 鸡排饭    │ │ 卤肉饭    │
│ $50      │ │ $80      │ │ $60      │
│ [加购物车]│ │ [加购物车]│ │ [加购物车]│
└──────────┘ └──────────┘ └──────────┘

                    [购物车 (3)]
                     ↓
                  [结账页面]
                     ↓
               [选择支付方式]
                     ↓
                  [提交订单]
                     ✅
```

---

## 📊 数据流程图

### 回馈金赚取流程

```
订单创建
   ↓
计算应付金额（扣除回馈金使用）
   ↓
应付金额 ÷ 店铺回馈比例 = 赚取点数
   ↓
创建 PointTransaction 记录（type='earn'）
   ↓
更新 User.points += 赚取点数
   ↓
完成
```

### 回馈金使用流程

```
用户选择使用 N 点
   ↓
验证：N ≤ User.points
   ↓
订单金额 - N = 应付金额
   ↓
创建 PointTransaction 记录（type='use', points=-N）
   ↓
更新 User.points -= N
   ↓
完成
```

### 访客点餐流程

```
扫描 QRCode
   ↓
/store/{shop_id}/table/{table_number}
   ↓
验证：shop.qrcode_enabled = true
   ↓
验证：table 存在
   ↓
显示商品列表
   ↓
选择商品 → 购物车
   ↓
提交订单（is_guest_order=true）
   ↓
更新 table.status = 'occupied'
   ↓
完成
```

---

## 🔧 故障排除

### 问题：QRCode 无法生成

**检查：**
1. `qrcode` 库是否安装：`pip list | grep qrcode`
2. 目录是否存在：`public/uploads/qrcodes/`
3. 目录是否可写

**解决：**
```bash
pip install qrcode==7.4.2
mkdir -p public/uploads/qrcodes
chmod 755 public/uploads/qrcodes
```

### 问题：支付金额验证失败

**原因：** 浮点数精度问题

**解决：** 使用整数（元），避免小数计算

```javascript
// 不好
const amount = 70.50 + 50.50; // 可能 = 121.00000001

// 好
const amount = Math.round((70.50 + 50.50) * 100) / 100; // = 121.00
```

### 问题：回馈金余额不正确

**检查：**
1. 查看 `point_transactions` 表
2. 检查最后一条记录的 `balance` 值
3. 对比 `user.points` 值

**修复：**
```sql
-- 重新计算用户回馈金
UPDATE user SET points = (
  SELECT COALESCE(SUM(points), 0) 
  FROM point_transactions 
  WHERE user_id = user.id
);
```

---

## 📞 技术支持

### 文档链接

- **系统就绪指南**：`docs/SYSTEM_READY.md`
- **实施完成报告**：`docs/IMPLEMENTATION_COMPLETE.md`
- **前端实施指南**：`docs/FRONTEND_IMPLEMENTATION_GUIDE.md`
- **进度报告**：`docs/LOYALTY_SYSTEM_PROGRESS.md`

### 代码位置

- **回馈金 API**：`app/routes/api/points.py`
- **桌号 API**：`app/routes/api/tables.py`
- **支付 API**：`app/routes/api/payment_methods.py`
- **订单增强**：`app/routes/api/orders.py`（底部）

---

## ✅ 验收标准

系统功能正常的标志：

- ✅ Backend 可以访问 `/backend/payment-methods`
- ✅ Store Admin 可以批量创建桌号
- ✅ QRCode 图片可以正常生成和查看
- ✅ QRCode 打印页面样式正确
- ✅ Customer 可以查看回馈金余额
- ✅ Customer 结账可以使用回馈金
- ✅ Customer 结账可以组合支付
- ✅ Guest 可以扫码点餐（无需登入）
- ✅ 所有 API 返回正确的 JSON
- ✅ 权限控制正常工作

---

<div align="center">

## 🎉 开始使用吧！

**所有功能已就绪，立即开始测试！**

📱 扫码点餐 | 🎁 回馈金 | 💳 组合支付

</div>

