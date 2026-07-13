/**
 * render.js - 自动从 issues.json 加载数据并渲染新闻列表
 * 支持中英文标题切换（使用 title_en 字段）
 * 增加缓存和加载状态优化
 */

(function() {
    // ---------- 缓存 key ----------
    const CACHE_KEY = 'news_data_cache';
    const CACHE_TIME_KEY = 'news_cache_time';
    const CACHE_DURATION = 5 * 60 * 1000; // 5分钟缓存

    // ---------- 容器选择逻辑 ----------
    function getContainer() {
        let el = document.getElementById('Recent-news');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'auto-render-container';
        document.body.appendChild(el);
        return el;
    }

    // ---------- 显示加载状态 ----------
    function showLoading(container) {
        container.innerHTML = '<p style="color:#666;font-style:italic;">⏳ Loading news...</p>';
    }

    // ---------- 格式化日期（支持中英文） ----------
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

    // ---------- HTML 转义 ----------
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ---------- 尝试从缓存加载 ----------
    function loadFromCache() {
        try {
            const cached = localStorage.getItem(CACHE_KEY);
            const cacheTime = localStorage.getItem(CACHE_TIME_KEY);
            if (cached && cacheTime) {
                const elapsed = Date.now() - parseInt(cacheTime);
                if (elapsed < CACHE_DURATION) {
                    return JSON.parse(cached);
                }
            }
        } catch (e) {
            // 忽略缓存错误
        }
        return null;
    }

    // ---------- 保存到缓存 ----------
    function saveToCache(data) {
        try {
            localStorage.setItem(CACHE_KEY, JSON.stringify(data));
            localStorage.setItem(CACHE_TIME_KEY, String(Date.now()));
        } catch (e) {
            // 忽略存储错误
        }
    }

    // ---------- 核心渲染函数 ----------
    function renderNews(lang) {
        const currentLang = lang || localStorage.getItem('lang') || 'en';
        const container = getContainer();
        
        // 显示加载状态
        showLoading(container);

        // 先尝试从缓存加载
        const cachedData = loadFromCache();
        if (cachedData && Array.isArray(cachedData) && cachedData.length > 0) {
            renderData(cachedData, currentLang, container);
            // 仍然在后台更新数据
            fetchData(currentLang, container, true);
            return;
        }

        // 没有缓存，从网络加载
        fetchData(currentLang, container, false);
    }

    // ---------- 获取数据 ----------
    function fetchData(lang, container, isBackground) {
        // 如果已经有全局数据
        if (typeof issuesData !== 'undefined' && Array.isArray(issuesData)) {
            renderData(issuesData, lang, container);
            saveToCache(issuesData);
            return;
        }

        fetch('data/issues.json')
            .then(response => {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    renderData(data, lang, container);
                    saveToCache(data);
                }
            })
            .catch(function(err) {
                console.error('加载 issues.json 失败:', err);
                // 如果缓存有数据，不要覆盖
                if (!isBackground && !container.querySelector('a')) {
                    container.innerHTML = '<p style="color:#c0392b;">⚠️ 数据加载失败，请刷新重试</p>';
                }
            });
    }

    // ---------- 实际渲染数据（优化为批量操作）----------
    function renderData(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('没有有效数据');
            return;
        }

        // 使用 slice 避免修改原数组
        const sorted = data.slice().sort(function(a, b) {
            return new Date(b.update_time) - new Date(a.update_time);
        });

        // 限制显示最近 20 条，减少 DOM 操作
        const limit = 20;
        const items = sorted.slice(0, limit);

        // 使用 DocumentFragment 批量构建 DOM
        const fragment = document.createDocumentFragment();
        
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            var date = formatDate(item.update_time, lang);
            var title = (lang === 'zh') ? item.title : (item.title_en || item.title);
            var safeTitle = escapeHtml(title);
            var safeUrl = escapeHtml(item.url);
            
            var b = document.createElement('b');
            b.textContent = date + ': ';
            
            var a = document.createElement('a');
            a.href = safeUrl;
            a.style.color = '#3BB9FF';
            a.style.textDecoration = 'none';
            a.style.wordBreak = 'break-all';
            a.textContent = safeTitle;
            
            var br = document.createElement('br');
            
            fragment.appendChild(b);
            fragment.appendChild(a);
            fragment.appendChild(br);
        }

        // 一次性更新 DOM
        container.innerHTML = '';
        container.appendChild(fragment);
    }

    // ---------- 暴露全局函数 ----------
    window.renderNews = renderNews;

    // ---------- 页面加载时自动执行 ----------
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            renderNews();
        });
    } else {
        renderNews();
    }

})();