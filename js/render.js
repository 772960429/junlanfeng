/**
 * render.js - 自动从内联数据或 issues.json 加载数据
 */

(function() {
    // ---------- 缓存 ----------
    const CACHE_KEY = 'news_data_cache';
    const CACHE_DURATION = 10 * 60 * 1000; // 10分钟

    function getContainer() {
        let el = document.getElementById('Recent-news');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'auto-render-container';
        document.body.appendChild(el);
        return el;
    }

    function formatDate(dateStr, lang) {
        const d = new Date(dateStr);
        if (isNaN(d)) return dateStr;
        const year = d.getFullYear();
        const month = d.getMonth() + 1;
        const day = d.getDate();
        if (lang === 'zh') {
            return year + '年' + month + '月' + day + '日';
        }
        return month + '/' + day + '/' + year;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function renderData(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) {
            return;
        }

        const sorted = data.slice().sort(function(a, b) {
            return new Date(b.update_time) - new Date(a.update_time);
        });

        // 最多显示 20 条
        const items = sorted.slice(0, 20);
        const fragment = document.createDocumentFragment();
        
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var date = formatDate(item.update_time, lang);
            var title = (lang === 'zh') ? item.title : (item.title_en || item.title);
            
            var b = document.createElement('b');
            b.textContent = date + ': ';
            
            var a = document.createElement('a');
            a.href = escapeHtml(item.url);
            a.style.color = '#3BB9FF';
            a.style.textDecoration = 'none';
            a.style.wordBreak = 'break-all';
            a.textContent = escapeHtml(title);
            
            var br = document.createElement('br');
            
            fragment.appendChild(b);
            fragment.appendChild(a);
            fragment.appendChild(br);
        }

        container.innerHTML = '';
        container.appendChild(fragment);
    }

    function renderNews(lang) {
        const currentLang = lang || localStorage.getItem('lang') || 'en';
        const container = getContainer();

        // 1. 优先使用内联数据（最快）
        if (typeof issuesData !== 'undefined' && Array.isArray(issuesData) && issuesData.length > 0) {
            renderData(issuesData, currentLang, container);
            // 保存到缓存供下次使用
            try {
                localStorage.setItem(CACHE_KEY, JSON.stringify(issuesData));
            } catch(e) {}
            return;
        }

        // 2. 尝试从缓存加载
        try {
            const cached = localStorage.getItem(CACHE_KEY);
            if (cached) {
                const data = JSON.parse(cached);
                if (Array.isArray(data) && data.length > 0) {
                    renderData(data, currentLang, container);
                    // 后台刷新
                    fetchData(currentLang, container);
                    return;
                }
            }
        } catch(e) {}

        // 3. 从远程加载
        container.innerHTML = '<p style="color:#666;">⏳ Loading news...</p>';
        fetchData(currentLang, container);
    }

    function fetchData(lang, container) {
        fetch('issues.json')
            .then(response => {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    renderData(data, lang, container);
                    try {
                        localStorage.setItem(CACHE_KEY, JSON.stringify(data));
                    } catch(e) {}
                }
            })
            .catch(function(err) {
                console.error('加载失败:', err);
                if (!container.querySelector('a')) {
                    container.innerHTML = '<p style="color:#c0392b;">⚠️ 数据加载失败</p>';
                }
            });
    }

    window.renderNews = renderNews;

    // 自动执行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            renderNews();
        });
    } else {
        renderNews();
    }
})();