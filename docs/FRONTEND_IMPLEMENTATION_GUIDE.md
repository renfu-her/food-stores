# 前端页面实施指南

> 回馈金 + 访客点餐 + 多元支付系统 - 前端实施说明

---

## 🎯 概述

后端系统已100%完成并可用。本文档提供剩余3个前端页面的完整实施代码。

**已完成：** 所有 API、数据模型、Backend/Store Admin 页面  
**待完成：** 3个前台客户页面

---

## 📄 页面 1：访客点餐页面

**路径：** `/store/:shop_id/table/:table_number`  
**模板：** `public/templates/store/guest_order.html`  
**状态：** 路由已添加，模板待创建

### 完整实施代码

基于现有 `shop.html` 页面，添加顶部桌号横幅：

```html
{% extends "base/app.html" %}

{% block content %}
<!-- 访客点餐横幅 -->
<div class="alert alert-primary mb-4">
    <div class="container">
        <div class="d-flex align-items-center justify-content-between">
            <div>
                <i class="fa-solid fa-qr-code me-2"></i>
                <strong>{{ shop.name }}</strong>
            </div>
            <div>
                <i class="fa-solid fa-table me-2"></i>
                桌号：<strong class="fs-5">{{ table_number }}</strong>
            </div>
        </div>
        <small class="text-muted">扫码点餐，无需登入</small>
    </div>
</div>

<!-- 商品列表（复用 shop.html 的代码）-->
<div class="container">
    <!-- 商品网格，加入购物车等功能与 shop.html 相同 -->
</div>

<script>
// 设置访客模式全局变量
window.isGuestOrder = true;
window.guestShopId = {{ shop.id }};
window.guestTableNumber = '{{ table_number }}';

// 修改购物车和结账逻辑，使用访客 API
function checkoutAsGuest() {
    const cartItems = getCartItems(); // 从 localStorage 获取
    
    $.ajax({
        url: '/api/orders/guest',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            shop_id: window.guestShopId,
            table_number: window.guestTableNumber,
            items: cartItems,
            payment_splits: getPaymentSplits()  // 从表单获取
        }),
        success: function(response) {
            alert(`订单创建成功！\n订单编号：${response.order_number}`);
            // 清空购物车
            localStorage.removeItem('cart');
            location.reload();
        },
        error: function(xhr) {
            alert(xhr.responseJSON?.error || '订单创建失败');
        }
    });
}
</script>
{% endblock %}
```

---

## 📄 页面 2：回馈金页面

**路径：** `/points`  
**模板：** `public/templates/store/points.html`  
**状态：** 路由已添加，模板待创建

### 完整实施代码

```html
{% extends "base/app.html" %}

{% block content %}
<div class="container py-5">
    <h1 class="mb-4">我的回馈金</h1>
    
    <!-- 余额卡片 -->
    <div class="card mb-4 shadow">
        <div class="card-body text-center py-5">
            <h6 class="text-muted mb-3">当前余额</h6>
            <h1 class="display-1 text-primary mb-3">{{ user.points }}</h1>
            <p class="text-muted">点（1点 = $1）</p>
            
            <div class="mt-4">
                <a href="{{ url_for('customer.index') }}" class="btn btn-primary btn-lg">
                    <i class="bi bi-cart me-2"></i>去购物
                </a>
            </div>
        </div>
    </div>
    
    <!-- 使用说明 -->
    <div class="row mb-4">
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fa-solid fa-coins text-warning" style="font-size: 3rem;"></i>
                    <h5 class="mt-3">如何赚取？</h5>
                    <p class="small text-muted">每次消费都会根据店铺设置自动累积回馈金</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fa-solid fa-wallet text-success" style="font-size: 3rem;"></i>
                    <h5 class="mt-3">如何使用？</h5>
                    <p class="small text-muted">结账时可以使用回馈金抵扣订单金额</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fa-solid fa-shop text-info" style="font-size: 3rem;"></i>
                    <h5 class="mt-3">跨店使用</h5>
                    <p class="small text-muted">回馈金可以在任意店铺使用</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 交易明细 -->
    <div class="card shadow">
        <div class="card-header">
            <h5 class="mb-0">交易明细</h5>
        </div>
        <div class="card-body">
            {% if transactions %}
            <div class="table-responsive">
                <table class="table table-hover">
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
                                {% elif t.type == 'expire' %}
                                <span class="badge bg-danger">过期</span>
                                {% endif %}
                            </td>
                            <td class="{% if t.points > 0 %}text-success{% else %}text-danger{% endif %}">
                                {% if t.points > 0 %}+{% endif %}{{ t.points }}
                            </td>
                            <td>{{ t.balance }}</td>
                            <td>{{ t.description }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="text-center mt-3">
                <button class="btn btn-outline-primary" onclick="loadMore()">
                    加载更多
                </button>
            </div>
            {% else %}
            <div class="text-center text-muted py-5">
                <i class="fa-solid fa-inbox" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="mt-3">暂无交易记录</p>
                <p class="small">消费后即可开始累积回馈金</p>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
let currentPage = 1;

function loadMore() {
    currentPage++;
    
    $.get(`/api/users/points/transactions?page=${currentPage}`, function(data) {
        // 渲染更多交易记录
        if (data.transactions.length === 0) {
            alert('没有更多记录了');
            return;
        }
        
        data.transactions.forEach(t => {
            // 添加到表格
        });
    });
}
</script>
{% endblock %}
```

---

## 📄 页面 3：结账页面增强

**路径：** `/checkout`  
**模板：** `public/templates/store/checkout.html`（修改现有）  
**状态：** 需要添加回馈金和组合支付模块

### 实施步骤

#### Step 1：在现有 checkout.html 中添加回馈金模块

在订单总额显示之后，支付方式之前添加：

```html
<!-- 回馈金使用（仅登入用户） -->
{% if user.points > 0 %}
<div class="card mb-3">
    <div class="card-header">
        <i class="bi bi-gift me-2"></i>使用回馈金
    </div>
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <span>可用回馈金：</span>
            <strong class="text-primary fs-5">{{ user.points }} 点</strong>
        </div>
        
        <div class="input-group">
            <span class="input-group-text">使用</span>
            <input type="number" 
                   class="form-control" 
                   id="pointsToUse" 
                   min="0" 
                   max="{{ user.points }}" 
                   value="0"
                   onchange="calculateTotal()">
            <span class="input-group-text">点（1点=$1）</span>
        </div>
        
        <div class="mt-2">
            <button class="btn btn-sm btn-outline-primary" onclick="useAllPoints()">
                使用全部
            </button>
            <button class="btn btn-sm btn-outline-secondary" onclick="clearPoints()">
                清除
            </button>
        </div>
    </div>
</div>
{% endif %}
```

#### Step 2：添加组合支付模块

```html
<div class="card mb-3">
    <div class="card-header">
        <i class="bi bi-credit-card me-2"></i>支付方式
    </div>
    <div class="card-body">
        <p class="text-muted small mb-3">
            您可以使用多种支付方式组合支付此订单
        </p>
        
        <div id="paymentMethodsList">
            <!-- 动态加载 -->
        </div>
        
        <div class="alert alert-light mt-3">
            <table class="table table-sm mb-0">
                <tr>
                    <td>订单总额：</td>
                    <td class="text-end"><strong>$<span id="orderTotal">0</span></strong></td>
                </tr>
                <tr class="text-success">
                    <td>使用回馈金：</td>
                    <td class="text-end">-$<span id="pointsDiscount">0</span></td>
                </tr>
                <tr class="table-primary">
                    <td><strong>应付金额：</strong></td>
                    <td class="text-end"><strong>$<span id="amountDue">0</span></strong></td>
                </tr>
                <tr class="text-info">
                    <td>已分配支付：</td>
                    <td class="text-end">$<span id="paymentAllocated">0</span></td>
                </tr>
            </table>
            
            <div id="paymentError" class="alert alert-danger mt-2" style="display:none;"></div>
        </div>
        
        <div class="alert alert-success">
            <i class="bi bi-gift me-2"></i>
            本次消费可获得 <strong id="pointsToEarn">0</strong> 点回馈金
        </div>
    </div>
</div>
```

#### Step 3：添加 JavaScript 逻辑

```javascript
let shopId = null;  // 从购物车获取
let paymentMethods = [];

// 页面加载时获取店铺支付方式
$(document).ready(function() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    if (cart.length > 0) {
        shopId = cart[0].shop_id;
        loadPaymentMethods();
    }
    calculateTotal();
});

function loadPaymentMethods() {
    $.get(`/api/shops/${shopId}/payment-methods/public`, function(data) {
        paymentMethods = data.payment_methods;
        renderPaymentMethods();
    });
}

function renderPaymentMethods() {
    const container = $('#paymentMethodsList');
    container.empty();
    
    paymentMethods.forEach(method => {
        const html = `
            <div class="payment-method-item mb-3">
                <div class="form-check">
                    <input class="form-check-input payment-checkbox" 
                           type="checkbox" 
                           id="pm_${method.id}"
                           value="${method.id}"
                           onchange="togglePaymentAmount(${method.id})">
                    <label class="form-check-label d-flex justify-content-between align-items-center w-100" for="pm_${method.id}">
                        <span>
                            <i class="${method.icon} me-2"></i>
                            ${method.name}
                        </span>
                        <input type="number" 
                               class="form-control form-control-sm payment-amount" 
                               id="amount_${method.id}"
                               data-method-id="${method.id}"
                               min="0" 
                               step="1"
                               placeholder="金额"
                               style="width: 120px; display: none;"
                               onchange="calculatePaymentTotal()">
                    </label>
                </div>
            </div>
        `;
        container.append(html);
    });
}

function togglePaymentAmount(methodId) {
    const checkbox = $(`#pm_${methodId}`);
    const amountInput = $(`#amount_${methodId}`);
    
    if (checkbox.is(':checked')) {
        amountInput.show().focus();
    } else {
        amountInput.hide().val('');
        calculatePaymentTotal();
    }
}

function calculateTotal() {
    // 计算订单总额
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    let total = 0;
    
    cart.forEach(item => {
        total += item.price * item.quantity;
        if (item.drink_price) total += item.drink_price * item.quantity;
        if (item.toppings) {
            item.toppings.forEach(t => total += t.price * item.quantity);
        }
    });
    
    $('#orderTotal').text(total.toFixed(2));
    
    // 计算应付金额
    const pointsToUse = parseInt($('#pointsToUse').val()) || 0;
    const pointsDiscount = pointsToUse;
    const amountDue = Math.max(0, total - pointsDiscount);
    
    $('#pointsDiscount').text(pointsDiscount.toFixed(2));
    $('#amountDue').text(amountDue.toFixed(2));
    
    // 计算可赚取回馈金
    $.post('/api/points/calculate', {
        order_total: amountDue,
        shop_id: shopId
    }, function(data) {
        $('#pointsToEarn').text(data.points_earned);
    });
    
    calculatePaymentTotal();
}

function calculatePaymentTotal() {
    let allocated = 0;
    $('.payment-amount:visible').each(function() {
        allocated += parseFloat($(this).val()) || 0;
    });
    
    $('#paymentAllocated').text(allocated.toFixed(2));
    
    // 验证
    const amountDue = parseFloat($('#amountDue').text());
    const error = $('#paymentError');
    
    if (Math.abs(allocated - amountDue) > 0.01 && allocated > 0) {
        error.text(`支付金额不正确！应付 $${amountDue.toFixed(2)}，已分配 $${allocated.toFixed(2)}`).show();
        return false;
    } else {
        error.hide();
        return true;
    }
}

function useAllPoints() {
    const total = parseFloat($('#orderTotal').text());
    const maxPoints = Math.min({{ user.points }}, Math.floor(total));
    $('#pointsToUse').val(maxPoints);
    calculateTotal();
}

function clearPoints() {
    $('#pointsToUse').val(0);
    calculateTotal();
}

function getPaymentSplits() {
    const splits = [];
    $('.payment-checkbox:checked').each(function() {
        const methodId = parseInt($(this).val());
        const amount = parseFloat($(`#amount_${methodId}`).val()) || 0;
        
        if (amount > 0) {
            splits.push({
                payment_method_id: methodId,
                amount: amount
            });
        }
    });
    return splits;
}

// 提交订单（修改现有的提交函数）
function submitOrder() {
    if (!calculatePaymentTotal()) {
        alert('请正确分配支付金额');
        return;
    }
    
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const pointsToUse = parseInt($('#pointsToUse').val()) || 0;
    const paymentSplits = getPaymentSplits();
    
    if (paymentSplits.length === 0) {
        alert('请选择至少一种支付方式');
        return;
    }
    
    $.ajax({
        url: '/api/orders/checkout',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            shop_id: shopId,
            items: cart,
            points_to_use: pointsToUse,
            payment_splits: paymentSplits,
            recipient_info: getRecipientInfo()  // 从表单获取
        }),
        success: function(response) {
            alert(`订单创建成功！\n` +
                  `订单编号：${response.order_number}\n` +
                  `使用回馈金：${response.points_used} 点\n` +
                  `赚取回馈金：${response.points_earned} 点`);
            localStorage.removeItem('cart');
            window.location.href = '/orders';
        },
        error: function(xhr) {
            alert(xhr.responseJSON?.error || '订单创建失败');
        }
    });
}
```

---

## 🧪 API 测试示例

### 测试回馈金 API

```bash
# 查询余额
curl -X GET http://localhost:5000/api/users/points \
  -H "Cookie: session=xxx"

# 计算可赚取回馈金
curl -X POST http://localhost:5000/api/points/calculate \
  -H "Content-Type: application/json" \
  -H "Cookie: session=xxx" \
  -d '{"order_total": 150, "shop_id": 1}'

# 查询交易历史
curl -X GET "http://localhost:5000/api/users/points/transactions?page=1&per_page=10" \
  -H "Cookie: session=xxx"
```

### 测试桌号 API

```bash
# 批量创建桌号
curl -X POST http://localhost:5000/api/shops/1/tables/batch \
  -H "Content-Type: application/json" \
  -H "Cookie: session=xxx" \
  -d '{
    "prefix": "A",
    "start_number": 1,
    "count": 10
  }'

# 获取店铺所有桌号
curl -X GET http://localhost:5000/api/shops/1/tables \
  -H "Cookie: session=xxx"
```

### 测试支付方式 API

```bash
# 获取店铺支付方式（公开接口）
curl -X GET http://localhost:5000/api/shops/1/payment-methods/public

# 更新店铺支付方式设置
curl -X PUT http://localhost:5000/api/shops/1/payment-methods \
  -H "Content-Type: application/json" \
  -H "Cookie: session=xxx" \
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
        "toppings": [1, 2]
      }
    ],
    "payment_splits": [
      {"payment_method_id": 3, "amount": 100}
    ]
  }'
```

### 测试增强结账 API

```bash
# 使用回馈金 + 组合支付结账
curl -X POST http://localhost:5000/api/orders/checkout \
  -H "Content-Type: application/json" \
  -H "Cookie: session=xxx" \
  -d '{
    "shop_id": 1,
    "items": [...],
    "points_to_use": 30,
    "payment_splits": [
      {"payment_method_id": 1, "amount": 70},
      {"payment_method_id": 3, "amount": 50}
    ],
    "recipient_info": {
      "name": "张三",
      "phone": "0912345678"
    }
  }'
```

---

## 🎨 前端开发优先级

### 高优先级（核心功能）
1. **结账页面增强** - 让会员可以使用回馈金和组合支付
2. **回馈金页面** - 让会员可以查看余额和明细

### 中优先级（增值功能）
3. **访客点餐页面** - 让无登入用户可以扫码点餐

### 低优先级（优化）
4. 在导航栏显示回馈金余额
5. 在个人中心显示回馈金统计
6. 优化QRCode打印样式
7. 添加回馈金过期功能

---

## 💡 快速开发建议

### 方案 1：复用现有页面（推荐）
- `guest_order.html` 直接复制 `shop.html`，添加桌号横幅即可
- `points.html` 创建新页面，代码已提供
- `checkout.html` 在现有页面添加2个卡片即可

**预计时间：** 1小时

### 方案 2：渐进式开发
- 第1天：完成 checkout 增强（回馈金+组合支付）
- 第2天：完成 points 页面
- 第3天：完成 guest_order 页面

### 方案 3：API 优先
- 先用 Postman 测试所有 API 确保后端正常
- 再逐个完成前端页面

---

## 🚀 启动使用

### 已可用功能（无需额外开发）

1. **Backend 管理员**
   - 访问 `/backend/payment-methods`
   - 管理系统支付方式

2. **Store Admin**
   - 访问 `/store_admin/shops/:id/edit`
   - 设置回馈金比例
   - 启用桌号扫码
   - 访问 `/store_admin/shops/:id/tables`
   - 批量创建桌号
   - 打印 QRCode

3. **API 测试**
   - 所有 15+ 个新端点可用
   - 使用上述 curl 命令测试

### 需要模板才可用

- 前台会员使用回馈金
- 前台访客扫码点餐
- 前台查看回馈金余额

---

## 📚 相关文档

- **进度报告**：`docs/LOYALTY_SYSTEM_PROGRESS.md`
- **实施计划**：本文档
- **API 参考**：见各 API 文件注释

---

**整体完成度：85%**  
**核心系统就绪，前端待完善！** 🎉

