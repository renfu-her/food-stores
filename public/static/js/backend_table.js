/**
 * Backend 数据表格管理器
 * 改进版本 - 使用类来避免全局变量冲突
 */

class DataTableManager {
    constructor(tableBodyId, items, renderFunction) {
        this.tableBodyId = tableBodyId;
        this.allItems = items || [];
        this.filteredItems = items || [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.renderFunction = renderFunction;
    }
    
    // 初始化
    init() {
        this.render();
        this.updatePagination();
    }
    
    // 渲染表格
    render() {
        const tbody = document.getElementById(this.tableBodyId);
        if (!tbody) {
            console.error('找不到表格元素:', this.tableBodyId);
            return;
        }
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const itemsToShow = this.filteredItems.slice(startIndex, endIndex);
        
        tbody.innerHTML = '';
        
        if (itemsToShow.length === 0) {
            tbody.innerHTML = '<tr><td colspan="100" class="text-center text-muted py-4">沒有數據</td></tr>';
            return;
        }
        
        itemsToShow.forEach(item => {
            tbody.innerHTML += this.renderFunction(item);
        });
        
        console.log(`✓ 渲染 ${itemsToShow.length} 筆數據`);
    }
    
    // 更新分页
    updatePagination() {
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        const paginationInfo = document.getElementById('paginationInfo');
        const paginationControls = document.getElementById('paginationControls');
        
        if (paginationInfo) {
            const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, this.filteredItems.length);
            paginationInfo.textContent = `顯示 ${startItem}-${endItem} / 共 ${this.filteredItems.length} 筆`;
        }
        
        if (paginationControls) {
            this.renderPaginationControls(totalPages);
        }
    }
    
    // 渲染分页控件
    renderPaginationControls(totalPages) {
        const controls = document.getElementById('paginationControls');
        let html = '';
        
        // 上一页
        html += `<li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="tableManager.changePage(${this.currentPage - 1}); return false;">上一頁</a>
        </li>`;
        
        // 页码
        const maxButtons = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="tableManager.changePage(1); return false;">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === this.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="tableManager.changePage(${i}); return false;">${i}</a>
            </li>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" onclick="tableManager.changePage(${totalPages}); return false;">${totalPages}</a></li>`;
        }
        
        // 下一页
        html += `<li class="page-item ${this.currentPage === totalPages || totalPages === 0 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="tableManager.changePage(${this.currentPage + 1}); return false;">下一頁</a>
        </li>`;
        
        controls.innerHTML = html;
    }
    
    // 切换页码
    changePage(page) {
        const totalPages = Math.ceil(this.filteredItems.length / this.itemsPerPage);
        if (page < 1 || page > totalPages) return;
        this.currentPage = page;
        this.render();
        this.updatePagination();
    }
    
    // 改变每页显示数量
    changeItemsPerPage(value) {
        this.itemsPerPage = parseInt(value);
        this.currentPage = 1;
        this.render();
        this.updatePagination();
    }
    
    // 搜索
    search(searchValue, searchFields) {
        if (!searchValue) {
            this.filteredItems = this.allItems;
        } else {
            const searchLower = searchValue.toLowerCase();
            this.filteredItems = this.allItems.filter(item => {
                return searchFields.some(field => {
                    const value = this.getNestedProperty(item, field);
                    return value && value.toString().toLowerCase().includes(searchLower);
                });
            });
        }
        this.currentPage = 1;
        this.render();
        this.updatePagination();
    }
    
    // 过滤
    filter(filterFn) {
        this.filteredItems = this.allItems.filter(filterFn);
        this.currentPage = 1;
        this.render();
        this.updatePagination();
    }
    
    // 获取嵌套属性
    getNestedProperty(obj, path) {
        return path.split('.').reduce((prev, curr) => prev && prev[curr], obj);
    }
}

// 全局变量（用于页面调用）
let tableManager = null;

