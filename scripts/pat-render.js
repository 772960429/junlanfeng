/**
 * pat-render.js - 从 patents.json 加载专利数据并渲染到 patents.html
 * 支持中英文切换和 localStorage 缓存
 */

(function() {
    'use strict';

    var CACHE_KEY = 'pat_data_cache';
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
        var citations = item.citations;

        // 被引用次数为空或 0 时不显示
        var hasCitations = isNumeric(citations) && parseFloat(citations) !== 0;

        if (lang === 'zh') {
            var detail = source;
            if (hasCitations) {
                detail += '；被引用次数：' + citations;
            }
            return detail;
        } else {
            var detail = source;
            if (hasCitations) {
                detail += ', ' + citations + ' Citations';
            }
            return detail;
        }
    }

    // 提取年份（兼容 2020 / '2020.0' / '2020年' / 日期字符串等）
    function extractYearNum(val) {
        if (!val) return 0;
        var m = String(val).match(/(?:19|20)\d{2}/);
        return m ? parseInt(m[0], 10) : 0;
    }

    // 专利号前缀分组：US 最前，EP/其他国家/组织次之，CN 最后；无空前缀兜底归入 CN 组
    function patentGroupRank(item) {
        var src = String(item.source_en || item.source_zh || '').toUpperCase();
        var m = src.match(/^([A-Z]+)/);
        var prefix = m ? m[1] : 'CN';
        if (prefix === 'US') return 0;
        if (prefix === 'CN') return 2;
        return 1; // EP / WO / 其他
    }

    // 提取专利号中的数字部分（US11194883B2 → 11194883）
    function patentNum(item) {
        var src = String(item.source_en || item.source_zh || '').toUpperCase();
        var m = src.match(/(\d+)/);
        return m ? parseInt(m[1], 10) : 0;
    }

    // 提取专利号末尾种类码（US11194883B2 → B2，CN122156733A → A）
    function patentKind(item) {
        var src = String(item.source_en || item.source_zh || '').toUpperCase();
        var m = src.match(/([A-Z]+\d*)$/);
        return m ? m[1] : '';
    }

    // 排序：1) 国别分组 US → EP/其他 → CN；2) 组内年份倒序；3) 年份相同按专利号数值降序；
    // 4) 号相同按种类码（B2 优先于 A1）；5) 最后按标题排序（中文拼音/英文字母，忽略大小写标点）
    function sortItems(data, lang) {
        var locale = (lang === 'zh') ? 'zh-Hans-CN' : 'en';
        return data.slice().sort(function(a, b) {
            // 1. 国别分组
            var ga = patentGroupRank(a);
            var gb = patentGroupRank(b);
            if (ga !== gb) return ga - gb;

            // 2. 年份倒序
            var ya = extractYearNum(a.year);
            var yb = extractYearNum(b.year);
            if (ya !== yb) return yb - ya;

            // 3. 专利号数值降序（号大在前）
            var na = patentNum(a);
            var nb = patentNum(b);
            if (na !== nb) return nb - na;

            // 4. 种类码降序（B2 在前，A1 在后）
            var ka = patentKind(a);
            var kb = patentKind(b);
            if (ka !== kb) return kb.localeCompare(ka);

            // 5. 兜底：标题升序
            var ta = (lang === 'zh') ? (a.title_zh || a.title_en || '') : (a.title_en || a.title_zh || '');
            var tb = (lang === 'zh') ? (b.title_zh || b.title_en || '') : (b.title_en || b.title_zh || '');
            return ta.localeCompare(tb, locale, { sensitivity: 'base', numeric: true, ignorePunctuation: true });
        });
    }

    // 渲染专利列表
    function renderPatents(data, lang, container) {
        if (!Array.isArray(data) || data.length === 0) return;

        data = sortItems(data, lang);

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
