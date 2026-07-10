/**
 * render.js - 自动从 issues.json 加载数据并渲染新闻列表
 * 支持中英文标题切换（使用 title_en 字段）
 * 用法：页面引入 <script src="render.js"></script>
 * 容器：id="Recent-news"
 */

(function() {
    // ---------- 容器选择逻辑（保持不变） ----------
    function getContainer() {
        let el = document.getElementById('Recent-news');
        if (el) return el;
        el = document.createElement('div');
        el.id = 'auto-render-container';
        document.body.appendChild(el);
        return el;
    }

    // ---------- 格式化日期 ----------
    function formatDate(dateStr) {
        const d = new Date(dateStr);
        if (isNaN(d)) return dateStr;
        return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
    }

    // ---------- HTML 转义 ----------
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ---------- 核心渲染函数（接受 lang 参数） ----------
    function renderNews(lang) {
        // 获取当前语言，如果未传入则从 localStorage 读取，默认 'en'
        const currentLang = lang || localStorage.getItem('lang') || 'en';
        const container = getContainer();

        // 如果数据已经作为全局变量存在（保留兼容）
        if (typeof issuesData !== 'undefined' && Array.isArray(issuesData)) {
            renderData(issuesData, currentLang, container);
            return;
        }

        // 否则 fetch 加载
        fetch('issues.json')
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => renderData(data, currentLang, container))
            .catch(err => {
                console.error('加载 issues.json 失败:', err);
                container.innerHTML = '<p style="color:red;">数据加载失败，请刷新重试。</p>';
            });
    }

    // ---------- 实际渲染数据的函数 ----------
    function renderData(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('没有有效数据');
            return;
        }

        // 按 update_time 降序（最新在前）
        const sorted = [...data].sort((a, b) =>
            new Date(b.update_time) - new Date(a.update_time)
        );

        let html = '';
        sorted.forEach(item => {
            const date = formatDate(item.update_time);
            // 根据语言选择标题：英文模式使用 title_en，中文使用 title，若无英文则 fallback 到 title
            const title = (lang === 'zh') ? item.title : (item.title_en || item.title);
            const safeTitle = escapeHtml(title);
            const safeUrl = escapeHtml(item.url);
            html += `<b>${date}</b>: ${safeTitle}<br> <a href="${safeUrl}" style="color: #3BB9FF; text-decoration: none;word-break: break-all;"> ${safeUrl}</a><br>`;
        });

        container.innerHTML = html; // 替换内容
    }

    // ---------- 暴露全局函数 ----------
    window.renderNews = renderNews;

    // ---------- 页面加载时自动执行 ----------
    // 确保 DOM 加载完毕
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => renderNews());
    } else {
        renderNews();
    }

})();