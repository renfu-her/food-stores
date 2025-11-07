/**
 * Backend 通用 JavaScript 功能
 * 包含分页、搜索、CRUD 等通用功能
 */

// 分页和搜索配置
let currentPage = 1;
let itemsPerPage = 10;
let allItems = [];
let filteredItems = [];

/**
 * 初始化数据表格
 * @param {string} tableBodyId - 表格 tbody 的 ID
 * @param {Array} items - 数据项数组
 * @param {Function} renderRowFunction - 渲染单行的函数
 */
function initializeDataTable(tableBodyId, items, renderRowFunction) {
    allItems = items;
    filteredItems = items;
    currentPage = 1;
    
    renderTable(tableBodyId, renderRowFunction);
    updatePagination();
}

/**
 * 渲染表格
 */
function renderTable(tableBodyId, renderRowFunction) {
    const tbody = document.getElementById(tableBodyId);
    if (!tbody) return;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const itemsToShow = filteredItems.slice(startIndex, endIndex);
    
    tbody.innerHTML = '';
    
    if (itemsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="100" class="text-center text-muted py-4">沒有數據</td></tr>';
        return;
    }
    
    itemsToShow.forEach(item => {
        tbody.innerHTML += renderRowFunction(item);
    });
}

/**
 * 更新分页信息
 */
function updatePagination() {
    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const paginationInfo = document.getElementById('paginationInfo');
    const paginationControls = document.getElementById('paginationControls');
    
    if (paginationInfo) {
        const startItem = (currentPage - 1) * itemsPerPage + 1;
        const endItem = Math.min(currentPage * itemsPerPage, filteredItems.length);
        paginationInfo.textContent = `顯示 ${startItem}-${endItem} / 共 ${filteredItems.length} 筆`;
    }
    
    if (paginationControls) {
        let html = '';
        
        // 上一页
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">上一頁</a>
        </li>`;
        
        // 页码
        const maxButtons = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
        let endPage = Math.min(totalPages, startPage + maxButtons - 1);
        
        if (endPage - startPage < maxButtons - 1) {
            startPage = Math.max(1, endPage - maxButtons + 1);
        }
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(1); return false;">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">${i}</a>
            </li>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" onclick="changePage(${totalPages}); return false;">${totalPages}</a></li>`;
        }
        
        // 下一页
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">下一頁</a>
        </li>`;
        
        paginationControls.innerHTML = html;
    }
}

/**
 * 改变页码
 */
function changePage(page) {
    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    window.currentRenderFunction();
    updatePagination();
}

/**
 * 改变每页显示数量
 */
function changeItemsPerPage(value) {
    itemsPerPage = parseInt(value);
    currentPage = 1;
    window.currentRenderFunction();
    updatePagination();
}

/**
 * 搜索过滤
 */
function searchItems(searchValue, searchFields) {
    if (!searchValue) {
        filteredItems = allItems;
    } else {
        const searchLower = searchValue.toLowerCase();
        filteredItems = allItems.filter(item => {
            return searchFields.some(field => {
                const value = getNestedProperty(item, field);
                return value && value.toString().toLowerCase().includes(searchLower);
            });
        });
    }
    currentPage = 1;
    window.currentRenderFunction();
    updatePagination();
}

/**
 * 获取嵌套属性
 */
function getNestedProperty(obj, path) {
    return path.split('.').reduce((prev, curr) => prev && prev[curr], obj);
}

/**
 * 显示确认删除对话框
 */
function confirmDelete(message, callback) {
    if (confirm(message || '確定要刪除嗎？')) {
        callback();
    }
}

/**
 * 显示成功消息
 */
function showSuccess(message) {
    alert(message);
    location.reload();
}

/**
 * 显示错误消息
 */
function showError(message) {
    alert('錯誤：' + message);
}

