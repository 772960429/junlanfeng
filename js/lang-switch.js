// 语言切换按钮点击事件
document.addEventListener('DOMContentLoaded', function() {
    // 初始化语言
    const lang = getCurrentLang();
    setLanguage(lang);
    
    // 绑定按钮事件
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const lang = this.dataset.lang;
            switchLanguage(lang);
        });
    });
});
