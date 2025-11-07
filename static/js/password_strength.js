/**
 * 密碼強度檢測 JavaScript 版本
 */

function checkPasswordStrength(password) {
    if (!password) {
        return {
            valid: false,
            strength: 'low',
            score: 0,
            message: '請輸入密碼',
            checks: {}
        };
    }
    
    let score = 0;
    const checks = {
        length: false,
        uppercase: false,
        lowercase: false,
        digit: false,
        special: false
    };
    
    // 1. 長度檢查
    if (password.length >= 8) {
        checks.length = true;
        score += 20;
    }
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 10;
    
    // 2. 大寫字母
    if (/[A-Z]/.test(password)) {
        checks.uppercase = true;
        score += 15;
        if ((password.match(/[A-Z]/g) || []).length >= 2) score += 5;
    }
    
    // 3. 小寫字母
    if (/[a-z]/.test(password)) {
        checks.lowercase = true;
        score += 15;
        if ((password.match(/[a-z]/g) || []).length >= 2) score += 5;
    }
    
    // 4. 數字
    if (/\d/.test(password)) {
        checks.digit = true;
        score += 15;
        if ((password.match(/\d/g) || []).length >= 2) score += 5;
    }
    
    // 5. 特殊符號
    if (/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]/.test(password)) {
        checks.special = true;
        score += 15;
        if ((password.match(/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]/g) || []).length >= 2) score += 10;
    }
    
    // 判斷強度等級
    let strength, valid, message, color;
    
    if (score >= 80) {
        strength = 'high';
        valid = true;
        message = '強度：高';
        color = 'success';
    } else if (score >= 60) {
        strength = 'middle';
        valid = true;
        message = '強度：中（可接受）';
        color = 'warning';
    } else {
        strength = 'low';
        valid = false;
        message = '強度：低（不符合要求）';
        color = 'danger';
    }
    
    return {
        valid: valid,
        strength: strength,
        score: score,
        message: message,
        color: color,
        checks: checks
    };
}

function renderPasswordStrengthMeter(inputId, meterId) {
    const input = document.getElementById(inputId);
    const meter = document.getElementById(meterId);
    
    if (!input || !meter) return;
    
    input.addEventListener('input', function() {
        const password = input.value;
        const result = checkPasswordStrength(password);
        
        // 更新進度條
        const percentage = Math.min(result.score, 100);
        let html = `
            <div class="mb-2">
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar bg-${result.color}" 
                         role="progressbar" 
                         style="width: ${percentage}%"
                         aria-valuenow="${percentage}" 
                         aria-valuemin="0" 
                         aria-valuemax="100"></div>
                </div>
            </div>
            <div class="small">
                <div class="text-${result.color} mb-2"><strong>${result.message}</strong></div>
                <div class="row g-2">
                    <div class="col-6">
                        <span class="${result.checks.length ? 'text-success' : 'text-muted'}">
                            <i class="bi bi-${result.checks.length ? 'check-circle-fill' : 'circle'}"></i> 長度 ≥ 8
                        </span>
                    </div>
                    <div class="col-6">
                        <span class="${result.checks.uppercase ? 'text-success' : 'text-muted'}">
                            <i class="bi bi-${result.checks.uppercase ? 'check-circle-fill' : 'circle'}"></i> 大寫字母
                        </span>
                    </div>
                    <div class="col-6">
                        <span class="${result.checks.lowercase ? 'text-success' : 'text-muted'}">
                            <i class="bi bi-${result.checks.lowercase ? 'check-circle-fill' : 'circle'}"></i> 小寫字母
                        </span>
                    </div>
                    <div class="col-6">
                        <span class="${result.checks.digit ? 'text-success' : 'text-muted'}">
                            <i class="bi bi-${result.checks.digit ? 'check-circle-fill' : 'circle'}"></i> 數字
                        </span>
                    </div>
                    <div class="col-6">
                        <span class="${result.checks.special ? 'text-success' : 'text-muted'}">
                            <i class="bi bi-${result.checks.special ? 'check-circle-fill' : 'circle'}"></i> 特殊符號
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        meter.innerHTML = html;
        
        // 存储验证结果供表单提交时使用
        input.dataset.passwordValid = result.valid;
        input.dataset.passwordStrength = result.strength;
    });
}

