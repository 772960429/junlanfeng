/**
 * render.js - 自动从 issues.json 加载数据并渲染朋友圈动态列表
 * 用法：在页面中引入 <script src="render.js"></script>
 * 容器：优先使用 id="Recent-news"，否则 id="content"，最后 fallback 到 body
 */

(function() {
    // ---------- 容器选择逻辑 ----------
    function getContainer() {
        let el = document.getElementById('Recent-news');
        if (el) return el;
        // 若都没有，创建新的 div 追加到 body
        el = document.createElement('div');
        el.id = 'auto-render-container';
        document.body.appendChild(el);
        return el;
    }

    // ---------- 格式化日期为 MM/DD/YYYY ----------
    function formatDate(dateStr) {
        const d = new Date(dateStr);
        if (isNaN(d)) return dateStr; // 无效日期则返回原样
        return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
    }

    // ---------- 简单的 HTML 转义 ----------
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ---------- 渲染主函数 ----------
    function render(data) {
        if (!Array.isArray(data) || data.length === 0) {
            console.warn('没有有效数据');
            return;
        }

        // 按 update_time 降序（最新在前）
        const sorted = [...data].sort((a, b) =>
            new Date(b.update_time) - new Date(a.update_time)
        );

        // 构建 HTML 字符串
        let html = '';
        sorted.forEach(item => {
            const date = formatDate(item.update_time);
            const safeTitle = escapeHtml(item.title);
            const safeUrl = escapeHtml(item.url);
            html += `<b>${date}</b>: ${safeTitle}<br> <a href="${safeUrl}" style="color: #3BB9FF; text-decoration: none;word-break: break-all;"> ${safeUrl}</a><br>`;
        });

        // 插入到容器
        const container = getContainer();
        container.innerHTML = html; // 清空并替换
    }

    // ---------- 加载数据 ----------
    // 如果数据已作为全局变量（如硬编码）存在则直接使用
    if (typeof issuesData !== 'undefined' && Array.isArray(issuesData)) {
        render(issuesData);
        return;
    }

    // 否则通过 fetch 加载同目录下的 issues.json
    fetch('issues.json')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => render(data))
        .catch(err => {
            console.error('加载 issues.json 失败:', err);
            // 错误提示（可选）
            const container = getContainer();
            container.innerHTML = '<p style="color:red;">数据加载失败，请刷新重试。</p>';
        });
})();