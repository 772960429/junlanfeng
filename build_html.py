#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_html.py - 从本地 JSON 文件构建带内联数据的 HTML
在构建阶段直接读取文件，不需要网络请求
"""

import json
import os
import sys
import re
from datetime import datetime

def load_json(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ 警告: {file_path} 不存在")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ 错误: {file_path} 格式不正确 - {e}")
        return []

def merge_data(issues_path='data/issues.json', extra_path='data/data.json'):
    """
    合并多个数据源
    
    Args:
        issues_path: issues.json 路径
        extra_path: 额外的数据文件路径（可选）
    """
    data = []
    
    # 1. 加载 issues
    issues = load_json(issues_path)
    if issues:
        data.extend(issues)
        print(f"📊 加载了 {len(issues)} 条 issues 数据")
    
    # 2. 加载额外数据（如果有）
    if os.path.exists(extra_path):
        extra = load_json(extra_path)
        if extra:
            data.extend(extra)
            print(f"📊 加载了 {len(extra)} 条额外数据")
    else:
        print(f"ℹ️ 额外数据文件 {extra_path} 不存在，跳过")
    
    # 3. 按 update_time 排序
    data.sort(key=lambda x: x.get('update_time', ''), reverse=True)
    
    print(f"📊 共合并 {len(data)} 条数据")
    return data

def generate_inline_js(data, variable_name='issuesData'):
    """生成内联 JavaScript 代码"""
    if not data:
        return f'var {variable_name} = [];'
    
    # 生成紧凑的 JSON（节省空间）
    json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return f'var {variable_name} = {json_str};'

def read_html(template_path='index.html'):
    """读取 HTML 模板"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 错误: 模板文件 {template_path} 不存在")
        return None

def inject_inline_data(html_content, inline_js, before_script='js/render.js'):
    """
    将内联数据注入到 HTML 中
    会先删除已有的内联数据，避免重复
    
    Args:
        html_content: HTML 内容
        inline_js: 要注入的 JavaScript 代码
        before_script: 在哪个 script 标签之前插入
    
    Returns:
        修改后的 HTML 内容
    """
    # 1. 删除所有 issuesData 相关的定义（多种匹配模式）
    patterns = [
        # 带 <script> 标签的完整定义
        r'<script>\s*var\s+issuesData\s*=\s*[^;]+;\s*</script>',
        r'<script>\s*const\s+issuesData\s*=\s*[^;]+;\s*</script>',
        r'<script>\s*let\s+issuesData\s*=\s*[^;]+;\s*</script>',
        # 裸变量定义（不带 script 标签）
        r'var\s+issuesData\s*=\s*[^;]+;',
        r'const\s+issuesData\s*=\s*[^;]+;',
        r'let\s+issuesData\s*=\s*[^;]+;',
        # window 对象
        r'window\.issuesData\s*=\s*[^;]+;',
    ]
    
    for pattern in patterns:
        html_content = re.sub(pattern, '', html_content, flags=re.DOTALL)
    
    # 2. 清理多余的空行（让生成的 HTML 更干净）
    html_content = re.sub(r'\n\s*\n\s*\n', '\n\n', html_content)
    
    # 3. 构建新的内联脚本
    inline_script = f'<script>\n{inline_js}\n</script>\n    '
    
    # 4. 在 render.js 之前插入
    script_tag = f'<script src="{before_script}"'
    
    if script_tag in html_content:
        html_content = html_content.replace(script_tag, inline_script + script_tag)
        print(f"✅ 内联数据已插入到 {before_script} 之前")
        return html_content
    
    # 5. 在 </head> 之前插入
    head_end = '</head>'
    if head_end in html_content:
        html_content = html_content.replace(head_end, inline_script + head_end)
        print("✅ 内联数据已插入到 </head> 之前")
        return html_content
    
    # 6. 添加到文件开头
    print("⚠️ 未找到合适的插入位置，添加到文件顶部")
    return f'<script>\n{inline_js}\n</script>\n' + html_content

def write_html(content, output_path='index.html'):
    """写入 HTML 文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 HTML 已保存到: {output_path}")

def build_html(issues_path='data/issues.json', 
               extra_path='data/data.json',
               template_path='index.html',
               output_path='index.html'):
    """
    主构建函数
    """
    print("🚀 开始构建 HTML...")
    print(f"   Issues 数据: {issues_path}")
    print(f"   额外数据: {extra_path if os.path.exists(extra_path) else '无'}")
    print(f"   模板: {template_path}")
    print(f"   输出: {output_path}")
    print()
    
    # 1. 合并数据
    data = merge_data(issues_path, extra_path)
    
    if not data:
        print("⚠️ 警告: 没有数据，将生成空列表")
    
    # 2. 生成内联 JavaScript
    inline_js = generate_inline_js(data)
    
    # 3. 读取模板
    html_content = read_html(template_path)
    if html_content is None:
        print("❌ 构建失败")
        return False
    
    # 4. 注入内联数据（会自动删除旧数据）
    html_content = inject_inline_data(html_content, inline_js)
    
    # 5. 写入文件
    write_html(html_content, output_path)
    
    # 6. 显示统计
    print()
    print("📈 构建统计:")
    print(f"   - 数据条数: {len(data)}")
    if data:
        print(f"   - 最新更新: {data[0].get('update_time', 'N/A')}")
        print(f"   - 最后一条: {data[-1].get('title', 'N/A')[:50]}...")
    print(f"   - HTML 大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    
    return True

def main():
    """主函数"""
    build_html(
        issues_path='data/issues.json',
        extra_path='data/data.json',
        template_path='index.html',
        output_path='index.html'
    )

if __name__ == '__main__':
    main()