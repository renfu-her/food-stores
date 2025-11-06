"""
初始化支付方式數據
確保系統有必需的現金支付方式
"""
from app import create_app, db
from app.models import PaymentMethod

def init_payment_methods():
    """初始化支付方式"""
    app = create_app()
    
    with app.app_context():
        # 檢查現金支付是否已存在
        cash_payment = PaymentMethod.query.filter_by(code='cash').first()
        
        if not cash_payment:
            print('創建現金支付方式...')
            cash_payment = PaymentMethod(
                name='現金',
                code='cash',
                icon='fa-solid fa-money-bill-1',
                display_order=99,  # 現金固定在最後
                is_active=True
            )
            db.session.add(cash_payment)
            db.session.commit()
            print('✓ 現金支付方式創建成功！')
        else:
            print('✓ 現金支付方式已存在')
            print(f'   ID: {cash_payment.id}')
            print(f'   名稱: {cash_payment.name}')
            print(f'   代碼: {cash_payment.code}')
            print(f'   狀態: {"啟用" if cash_payment.is_active else "禁用"}')
        
        # 顯示所有支付方式
        all_methods = PaymentMethod.query.order_by(PaymentMethod.display_order).all()
        print(f'\n目前系統中共有 {len(all_methods)} 種支付方式：')
        for pm in all_methods:
            status = '✓ 啟用' if pm.is_active else '✗ 禁用'
            required = ' [必需]' if pm.code == 'cash' else ''
            print(f'  • {pm.name} ({pm.code}) - {status}{required}')

if __name__ == '__main__':
    print('='*60)
    print('初始化支付方式')
    print('='*60)
    print('')
    
    init_payment_methods()
    
    print('')
    print('='*60)
    print('初始化完成！')
    print('='*60)
    print('')
    print('提示：')
    print('  • 現金支付是系統必需的支付方式')
    print('  • 現金支付不能被刪除或禁用')
    print('  • 您可以在 Backend 管理頁面添加其他支付方式')
    print('')

