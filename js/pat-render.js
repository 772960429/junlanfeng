/**
 * pat-render.js - 从 patents.json 加载专利数据并渲染到 patents.html
 * 支持中英文切换和 localStorage 缓存
 */

(function() {
    'use strict';

    var CACHE_KEY = 'pat_data_cache';
    var CACHE_DURATION = 60 * 60 * 1000; // 1小时

    // 构建详情文本
    function buildDetail(item, lang) {
        var source = (lang === 'zh') ? item.source_zh : item.source_en;
        var citations = item.citations || '0';

        if (lang === 'zh') {
            return source + '；被引用次数：' + citations;
        } else {
            return source + ', ' + citations + ' Citations.';
        }
    }

    // 渲染专利列表
    function renderPatents(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) return;

        var fragment = document.createDocumentFragment();

        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            var title = (lang === 'zh') ? item.title_zh : (item.title_en || item.title_zh);
            var detail = buildDetail(item, lang);

            var li = document.createElement('li');
            var p = document.createElement('p');

            // 专利标题
            var patSpan = document.createElement('span');
            patSpan.className = 'pat';
            patSpan.textContent = title;
            p.appendChild(patSpan);

            p.appendChild(document.createElement('br'));

            // 详情
            var detailSpan = document.createElement('span');
            detailSpan.className = 'pat.detail';
            detailSpan.textContent = detail;
            p.appendChild(detailSpan);

            p.appendChild(document.createElement('br'));

            // PDF 链接（空值隐藏）
            if (item.pdf) {
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
    function renderPat(lang) {
        var currentLang = lang || (typeof window.getCurrentLang === 'function' ? window.getCurrentLang() : (localStorage.getItem('lang') || 'en'));
        var container = document.querySelector('ul.biblist');
        if (!container) return;

        // 1. 优先使用内联数据（file:// 协议下 fetch 不可用）
        if (typeof patentsData !== 'undefined' && Array.isArray(patentsData) && patentsData.length > 0) {
            renderPatents(patentsData, currentLang, container);
            // setCache(patentsData); // 缓存已临时禁用（性能测试）
            return;
        }

        // 2. 缓存已临时禁用（性能测试）
        // if (isCacheValid()) {
        //     var data = getCachedData();
        //     if (data) {
        //         renderPatents(data, currentLang, container);
        //         return;
        //     }
        // }

        // 3. 从 JSON 文件加载（需 HTTP 服务器）
        fetch('data/patents.json')
            .then(function(response) {
                if (!response.ok) throw new Error('HTTP ' + response.status);
                return response.json();
            })
            .then(function(data) {
                if (Array.isArray(data) && data.length > 0) {
                    renderPatents(data, currentLang, container);
                    // setCache(data); // 缓存已临时禁用（性能测试）
                }
            })
            .catch(function(err) {
                console.error('专利数据加载失败:', err);
            });
    }

    // 暴露给 i18n.js 调用
    window.renderPat = renderPat;

    // 自动初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            renderPat();
        });
    } else {
        renderPat();
    }
})();
