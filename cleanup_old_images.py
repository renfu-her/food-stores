"""
清理舊格式圖片工具
遍歷 uploads 目錄，刪除所有非 .webp 格式的圖片文件
"""
import os
from pathlib import Path

def get_uploads_dir():
    """獲取 uploads 目錄（優先使用根目錄的 uploads，否則使用 public/uploads）"""
    BASE_DIR = Path(__file__).parent
    uploads_dir = BASE_DIR / 'uploads'
    uploads_dir_public = BASE_DIR / 'public' / 'uploads'
    
    if uploads_dir.exists():
        return uploads_dir
    elif uploads_dir_public.exists():
        return uploads_dir_public
    else:
        return None

def cleanup_old_images():
    """清理所有非 WebP 格式的舊圖片"""
    
    # 定義 uploads 目錄
    uploads_dir = get_uploads_dir()
    
    if not uploads_dir or not uploads_dir.exists():
        print(f"❌ 目錄不存在: {uploads_dir}")
        print("   請確認 uploads 目錄是否存在（根目錄或 public/ 下）")
        return
    
    # 支持的舊圖片格式
    old_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    # 統計數據
    stats = {
        'total_scanned': 0,
        'deleted': 0,
        'kept_webp': 0,
        'errors': 0,
        'deleted_files': []
    }
    
    print("🔍 開始掃描圖片文件...")
    print(f"📁 掃描目錄: {uploads_dir}\n")
    
    # 遞歸遍歷所有文件
    for root, dirs, files in os.walk(uploads_dir):
        for filename in files:
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()
            stats['total_scanned'] += 1
            
            if ext == '.webp':
                # 保留 WebP 文件
                stats['kept_webp'] += 1
            elif ext in old_extensions:
                # 刪除舊格式圖片
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    stats['deleted'] += 1
                    stats['deleted_files'].append({
                        'path': str(file_path.relative_to(uploads_dir)),
                        'size': file_size
                    })
                    print(f"✅ 已刪除: {file_path.relative_to(uploads_dir)} ({file_size / 1024:.2f} KB)")
                except Exception as e:
                    stats['errors'] += 1
                    print(f"❌ 刪除失敗: {file_path.relative_to(uploads_dir)} - {str(e)}")
    
    # 顯示統計結果
    print("\n" + "="*60)
    print("📊 清理完成統計")
    print("="*60)
    print(f"📁 掃描文件總數: {stats['total_scanned']}")
    print(f"🗑️  已刪除舊格式: {stats['deleted']}")
    print(f"✅ 保留 WebP: {stats['kept_webp']}")
    print(f"❌ 錯誤數量: {stats['errors']}")
    
    if stats['deleted'] > 0:
        total_freed = sum(f['size'] for f in stats['deleted_files'])
        print(f"💾 釋放空間: {total_freed / 1024 / 1024:.2f} MB")
        print("\n已刪除的文件列表:")
        for f in stats['deleted_files']:
            print(f"  - {f['path']} ({f['size'] / 1024:.2f} KB)")
    
    print("\n✅ 清理完成！")

def preview_old_images():
    """預覽將要刪除的舊圖片（不實際刪除）"""
    
    uploads_dir = get_uploads_dir()
    
    if not uploads_dir or not uploads_dir.exists():
        print(f"❌ 目錄不存在: {uploads_dir}")
        print("   請確認 uploads 目錄是否存在（根目錄或 public/ 下）")
        return
    
    old_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    old_files = []
    
    print("🔍 預覽模式：掃描舊格式圖片...\n")
    
    for root, dirs, files in os.walk(uploads_dir):
        for filename in files:
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()
            
            if ext in old_extensions:
                file_size = file_path.stat().st_size
                old_files.append({
                    'path': str(file_path.relative_to(uploads_dir)),
                    'size': file_size
                })
    
    if not old_files:
        print("✅ 沒有找到舊格式圖片！")
        return
    
    print(f"📊 找到 {len(old_files)} 個舊格式圖片：\n")
    total_size = 0
    for f in old_files:
        print(f"  - {f['path']} ({f['size'] / 1024:.2f} KB)")
        total_size += f['size']
    
    print(f"\n💾 總大小: {total_size / 1024 / 1024:.2f} MB")
    print(f"\n⚠️  執行 cleanup_old_images() 將刪除這些文件")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        # 預覽模式
        preview_old_images()
    elif len(sys.argv) > 1 and sys.argv[1] == '--clean':
        # 清理模式
        confirm = input("⚠️  確定要刪除所有舊格式圖片嗎？ (yes/no): ")
        if confirm.lower() == 'yes':
            cleanup_old_images()
        else:
            print("❌ 已取消操作")
    else:
        print("""
圖片清理工具使用說明
===================

預覽模式（不刪除）：
    python cleanup_old_images.py --preview

清理模式（刪除舊圖片）：
    python cleanup_old_images.py --clean

說明：
- 此工具會掃描 uploads 目錄（優先根目錄，否則 public/uploads）
- 刪除所有非 WebP 格式的圖片（.jpg, .jpeg, .png, .gif, .bmp）
- 保留所有 .webp 格式的圖片
- 建議先使用 --preview 預覽將要刪除的文件
        """)

