/**
 * 从 issues.json 生成朋友圈动态列表
 * 使用方式：在 HTML 中引入此脚本，或直接运行（需服务器环境）
 */

// 自动加载并渲染
(function() {
    // 如果数据已经作为全局变量存在（如嵌入脚本），则直接渲染
    if (typeof issuesData !== 'undefined' && Array.isArray(issuesData)) {
        render(issuesData);
        return;
    }

    // 否则从同目录的 issues.json 获取
    fetch('issues.json')
        .then(response => {
            if (!response.ok) throw new Error('无法加载数据文件');
            return response.json();
        })
        .then(data => render(data))
        .catch(err => console.error('加载失败:', err));
})();

/**
 * 格式化日期为 MM/DD/YYYY（无前导零）
 */
function formatDate(dateStr) {
    const d = new Date(dateStr);
    const month = d.getMonth() + 1;   // 1-12
    const day = d.getDate();          // 1-31
    const year = d.getFullYear();
    return `${month}/${day}/${year}`;
}

/**
 * 渲染列表
 */
function render(data) {
    // 按 update_time 降序（最新的在前）
    const sorted = [...data].sort((a, b) => 
        new Date(b.update_time) - new Date(a.update_time)
    );

    let html = '';
    sorted.forEach(item => {
        const date = formatDate(item.update_time);
        // 转义标题中的特殊字符（避免 XSS）
        const safeTitle = escapeHtml(item.title);
        const safeUrl = escapeHtml(item.url);
        html += `<b>${date}: <a href="${safeUrl}" style="color: #3BB9FF; text-decoration: none;">${safeTitle}</a></b><br>`;
    });

    // 将结果插入到页面中 id 为 "content" 的元素，若不存在则追加到 body
    const container = document.getElementById('content') || document.body;
    container.innerHTML = html;
}

/**
 * 简单的 HTML 转义（防止 XSS）
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}