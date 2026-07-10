// 语言切换逻辑
function getCurrentLang() {
    return localStorage.getItem('lang') || 'en';
}

function setLanguage(lang) {
    localStorage.setItem('lang', lang);
    document.documentElement.lang = lang;

    // 更新 data-i18n 元素
    document.querySelectorAll('[data-i18n]').forEach(function(el) {
        var key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.hasAttribute('placeholder')) {
                    el.placeholder = translations[lang][key];
                } else {
                    el.value = translations[lang][key];
                }
            } else {
                el.innerHTML = translations[lang][key];
            }
        }
    });

    // 更新按钮状态
    document.querySelectorAll('.lang-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // 重新渲染新闻（如果 renderNews 存在）
    if (typeof window.renderNews === 'function') {
        window.renderNews(lang);
    }
}

function switchLanguage(lang) {
    if (lang === getCurrentLang()) return;
    setLanguage(lang);
}

// 页面加载后绑定按钮事件
document.addEventListener('DOMContentLoaded', function() {
    var lang = getCurrentLang();
    setLanguage(lang);  // 初始化界面

    document.querySelectorAll('.lang-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var lang = this.dataset.lang;
            switchLanguage(lang);
        });
    });
});