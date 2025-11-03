// SocketIO客户端脚本
(function() {
    let socket = null;
    
    function initSocket() {
        // 初始化Socket.IO连接
        socket = io();
        
        socket.on('connect', function() {
            console.log('Socket.IO connected');
        });
        
        socket.on('disconnect', function() {
            console.log('Socket.IO disconnected');
        });
        
        socket.on('connected', function(data) {
            console.log('Connected:', data);
        });
        
        socket.on('error', function(data) {
            console.error('Socket.IO error:', data);
        });
        
        // 订单更新事件
        socket.on('order_updated', function(data) {
            console.log('Order updated:', data);
            // 触发自定义事件，让页面可以监听
            window.dispatchEvent(new CustomEvent('orderUpdated', { detail: data }));
        });
        
        // 产品更新事件
        socket.on('product_updated', function(data) {
            console.log('Product updated:', data);
            window.dispatchEvent(new CustomEvent('productUpdated', { detail: data }));
        });
        
        // 产品状态变更事件
        socket.on('product_status_changed', function(data) {
            console.log('Product status changed:', data);
            window.dispatchEvent(new CustomEvent('productStatusChanged', { detail: data }));
        });
        
        // 新订单通知
        socket.on('new_order', function(data) {
            console.log('New order:', data);
            window.dispatchEvent(new CustomEvent('newOrder', { detail: data }));
        });
        
        // 加入店铺频道
        window.joinShopChannel = function(shopId) {
            if (socket) {
                socket.emit('join_shop', { shop_id: shopId });
            }
        };
        
        // 离开店铺频道
        window.leaveShopChannel = function(shopId) {
            if (socket) {
                socket.emit('leave_shop', { shop_id: shopId });
            }
        };
    }
    
    // 页面加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSocket);
    } else {
        initSocket();
    }
})();

