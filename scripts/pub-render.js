/**
 * pub-render.js - 从 publications.json 加载论文数据并渲染到 publications.html
 * 支持中英文切换和 localStorage 缓存
 */

(function() {
    'use strict';

    var CACHE_KEY = 'pub_data_cache';
    var CACHE_DURATION = 60 * 60 * 1000; // 1小时

    // 判断值是否为数字
    function isNumeric(val) {
        if (val === null || val === undefined || val === '') return false;
        var n = parseFloat(val);
        return !isNaN(n) && isFinite(n);
    }

    // 构建详情文本
    function buildDetail(item, lang) {
        var source = (lang === 'zh') ? item.source_zh : item.source_en;
        var year = item.year;
        // 被引用次数始终显示（包括 0），空值兜底为 0
        var citations = (item.citations === undefined || item.citations === null || item.citations === '') ? '0' : item.citations;
        var impactFactor = item.impact_factor;

        if (lang === 'zh') {
            var detail = source + '，' + year + '；被引用次数：' + citations;
            if (isNumeric(impactFactor)) {
                detail += '；影响因子：' + impactFactor;
            }
            detail += '。';
            return detail;
        } else {
            var detail = source + ', ' + year + '; ' + citations + ' citations';
            if (isNumeric(impactFactor)) {
                detail += '; Impact Factor: ' + impactFactor;
            }
            detail += '.';
            return detail;
        }
    }

    // 提取年份（兼容 2020 / '2020.0' / '2020年' / 日期字符串等）
    function extractYearNum(val) {
        if (!val) return 0;
        var m = String(val).match(/(?:19|20)\d{2}/);
        return m ? parseInt(m[0], 10) : 0;
    }

    // 排序：年份倒序；年份相同按英文标题字母排序（中英文模式一致，忽略大小写/标点）
    function sortItems(data) {
        return data.slice().sort(function(a, b) {
            var ya = extractYearNum(a.year);
            var yb = extractYearNum(b.year);
            if (ya !== yb) return yb - ya; // 年份倒序
            var ta = a.title_en || a.title_zh || '';
            var tb = b.title_en || b.title_zh || '';
            return ta.localeCompare(tb, 'en', { sensitivity: 'base', numeric: true, ignorePunctuation: true });
        });
    }

    // 渲染论文列表
    function renderPapers(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) return;

        data = sortItems(data);

        var fragment = document.createDocumentFragment();

        for (let i = 0; i < data.length; i++) {
            const item = data[i];
            var title = (lang === 'zh') ? item.title_zh : (item.title_en || item.title_zh);
            var detail = buildDetail(item, lang);

            var li = document.createElement('li');
            var p = document.createElement('p');

            // 论文标题
            var pubSpan = document.createElement('span');
            pubSpan.className = 'pub';
            pubSpan.textContent = title;
            p.appendChild(pubSpan);

            p.appendChild(document.createElement('br'));

            // 详情
            var detailSpan = document.createElement('span');
            detailSpan.className = 'pub.detail';
            detailSpan.textContent = detail;
            p.appendChild(detailSpan);

            p.appendChild(document.createElement('br'));

            // BibTeX 链接（空值隐藏）：新标签页以纯文本形式显示 BibTeX 内容
            if (item.bibtex) {
                var bibtexLink = document.createElement('a');
                bibtexLink.href = 'bibtex.html#' + encodeURIComponent(item.bibtex);
                bibtexLink.target = '_blank';
                bibtexLink.rel = 'noopener noreferrer';
                bibtexLink.className = 'link';
                bibtexLink.textContent = '[BibTeX]';
                bibtexLink.addEventListener('click', function(e) {
                    e.preventDefault();
                    try {
                        // 以 text/plain 打开，浏览器原生渲染（与 .bib 文件显示一致）
                        var blob = new Blob([item.bibtex], { type: 'text/plain;charset=utf-8' });
                        var url = URL.createObjectURL(blob);
                        window.open(url, '_blank', 'noopener');
                        setTimeout(function() { URL.revokeObjectURL(url); }, 60000);
                    } catch (err) {
                        // 兜底：跳转 bibtex.html 显示
                        window.open(this.href, '_blank', 'noopener');
                    }
                });
                p.appendChild(bibtexLink);

                if (item.pdf) {
                    p.appendChild(document.createTextNode(' '));
                }
            }

            // PDF 链接（空值或非 URL 隐藏）
            if (item.pdf && /^https?:\/\//i.test(item.pdf)) {
                var pdfLink = document.createElement('a');
                pdfLink.href = item.pdf;
                pdfLink.target = '_blank';
                pdfLink.rel = 'noopener noreferrer';
                pdfLink.className = 'link';
                pdfLink.textContent = '[PDF]';
                p.appendChild(pdfLink);
            }

            li.appendChild(p);
            fragment.appendChild(li);
        }

        container.innerHTML = '';
        container.appendChild(fragment);
    }

    // 缓存操作
    function isCacheValid() {
        var cached = localStorage.getItem(CACHE_KEY);
        if (!cached) return false;
        try {
            var obj = JSON.parse(cached);
            return Date.now() - obj.timestamp < CACHE_DURATION;
        } catch (e) {
            return false;
        }
    }

    function getCachedData() {
        try {
            var cached = localStorage.getItem(CACHE_KEY);
            return cached ? JSON.parse(cached).data : null;
        } catch (e) {
            return null;
        }
    }

    function setCache(data) {
        try {
            localStorage.setItem(CACHE_KEY, JSON.stringify({
                timestamp: Date.now(),
                data: data
            }));
        } catch (e) {}
    }

    // 主渲染函数
    function renderPub(lang) {
        var currentLang = lang || (typeof window.getCurrentLang === 'function' ? window.getCurrentLang() : (localStorage.getItem('lang') || 'en'));
        var container = document.querySelector('ul.biblist');
        if (!container) return;

        // 1. 优先使用内联数据（file:// 协议下 fetch 不可用）
        if (typeof publicationsData !== 'undefined' && Array.isArray(publicationsData) && publicationsData.length > 0) {
            renderPapers(publicationsData, currentLang, container);
            // setCache(publicationsData); // 缓存已临时禁用（性能测试）
            return;
        }

        // 2. 缓存已临时禁用（性能测试）
        // if (isCacheValid()) {
        //     var data = getCachedData();
        //     if (data) {
        //         renderPapers(data, currentLang, container);
        //         return;
        //     }
        // }

        // 3. 从 JSON 文件加载（需 HTTP 服务器）
        fetch('data/publications.json')
            .then(function(response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(function(data) {
                if (Array.isArray(data) && data.length > 0) {
                    renderPapers(data, currentLang, container);
                    // setCache(data); // 缓存已临时禁用（性能测试）
                }
            })
            .catch(function(err) {
                console.error('论文数据加载失败:', err);
            });
    }

    // 暴露给 i18n.js 调用
    window.renderPub = renderPub;

    // 自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            renderPub();
        });
    } else {
        renderPub();
    }
})();
