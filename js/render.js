/**
 * render.js - 自动从 issues.json 加载数据并渲染新闻列表
 * 支持中英文标题切换（使用 title_en 字段）
 * 用法：页面引入 <script src="render.js"></script>
 * 容器：id="Recent-news"
 */

(function() {
    // ---------- 容器选择逻辑 ----------
    function getContainer() {
        let el = document.getElementById('Recent-news');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'auto-render-container';
        document.body.appendChild(el);
        return el;
    }

    // ---------- 格式化日期（支持中英文） ----------
    function formatDate(dateStr, lang) {
        const d = new Date(dateStr);
        if (isNaN(d)) return dateStr;

        const year = d.getFullYear();
        const month = d.getMonth() + 1;
        const day = d.getDate();

        // 中文：2026年6月30日
        if (lang === 'zh') {
            return year + '年' + month + '月' + day + '日';
        }

        // 英文：月/日/年
        return month + '/' + day + '/' + year;
    }

    // ---------- HTML 转义 ----------
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ---------- 核心渲染函数 ----------
    function renderNews(lang) {
        const currentLang = lang || localStorage.getItem('lang') || 'en';
        const container = getContainer();

        if (typeof issuesData !== 'undefined' && Array.isArray(issuesData)) {
            renderData(issuesData, currentLang, container);
            return;
        }

        fetch('issues.json')
            .then(response => {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(data => renderData(data, currentLang, container))
            .catch(function(err) {
                console.error('加载 issues.json 失败:', err);
                container.innerHTML = '<p style="color:red;">数据加载失败，请刷新重试。</p>';
            });
    }

    // ---------- 实际渲染数据 ----------
    function renderData(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('没有有效数据');
            return;
        }

        const sorted = [].concat(data).sort(function(a, b) {
            return new Date(b.update_time) - new Date(a.update_time);
        });

        var html = '';
        for (var i = 0; i < sorted.length; i++) {
            var item = sorted[i];
            // 传入 lang 参数，让日期格式化支持中英文
            var date = formatDate(item.update_time, lang);
            var title = (lang === 'zh') ? item.title : (item.title_en || item.title);
            var safeTitle = escapeHtml(title);
            var safeUrl = escapeHtml(item.url);
            html += '<b>' + date + '</b><a href="' + safeUrl + '" style="color: #3BB9FF; text-decoration: none;word-break: break-all;">: ' + safeTitle + '</a><br>';
        }

        container.innerHTML = html;
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