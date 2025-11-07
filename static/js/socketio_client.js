// SocketIO客户端脚本
(function() {
    let socket = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    
    function initSocket() {
        // 初始化Socket.IO连接，添加重连配置
        socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
            timeout: 20000,
            transports: ['polling', 'websocket']
        });
        
        socket.on('connect', function() {
            console.log('Socket.IO connected');
            reconnectAttempts = 0;
        });
        
        socket.on('disconnect', function(reason) {
            console.log('Socket.IO disconnected:', reason);
            if (reason === 'io server disconnect') {
                // 服务器主动断开，尝试重连
                socket.connect();
            }
        });
        
        socket.on('connect_error', function(error) {
            reconnectAttempts++;
            console.warn('Socket.IO connection error:', error.message);
            if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                console.error('Socket.IO max reconnection attempts reached');
            }
        });
        
        socket.on('reconnect', function(attemptNumber) {
            console.log('Socket.IO reconnected after', attemptNumber, 'attempts');
            reconnectAttempts = 0;
        });
        
        socket.on('reconnect_attempt', function(attemptNumber) {
            console.log('Socket.IO reconnection attempt:', attemptNumber);
        });
        
        socket.on('reconnect_error', function(error) {
            console.warn('Socket.IO reconnection error:', error.message);
        });
        
        socket.on('reconnect_failed', function() {
            console.error('Socket.IO reconnection failed');
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

