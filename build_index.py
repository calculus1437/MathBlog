import os
import re
import json
from datetime import datetime

# 简易解析 _config.yml
def load_config():
    config = {
        'title': "calculus_1437's Math Notes",
        'description': "纯净的 HTML 数学笔记博客"
    }
    if not os.path.exists('_config.yml'): return config
    
    current_list_key = None
    with open('_config.yml', 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'): continue
            
            # 解析列表项 (例如: - calculus1437)
            if stripped.startswith('- ') and current_list_key:
                config[current_list_key].append(stripped[2:].strip().strip("'\""))
                continue
                
            if ':' in stripped:
                k, v = stripped.split(':', 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if not v:
                    # 值为空表示接下来是列表
                    config[k] = []
                    current_list_key = k
                else:
                    config[k] = v
                    current_list_key = None
    return config

SITE_CONFIG = load_config()

# 配置路径
POSTS_DIR = 'posts'
INDEX_FILE = 'index.html'

def enhance_post(file_path):
    """为文章添加悬浮目录和返回主页的导航，增强在线浏览体验"""
    import re
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        # 恢复使用稳定且不限制 CORS 的 cdnjs 或者 unpkg，避免 staticfile 的加载/阻塞问题
        new_content = re.sub(
            r'href="file:///[^"]+katex\.min\.css"',
            r'href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css"',
            new_content
        )
        new_content = re.sub(
            r'href="https://cdn\.staticfile\.net/KaTeX/0\.16\.8/katex\.min\.css"',
            r'href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css"',
            new_content
        )
        new_content = re.sub(
            r'href="https://cdn\.jsdelivr\.net/npm/katex@0\.16\.8/dist/katex\.min\.css"',
            r'href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css"',
            new_content
        )
            
        # 让已注入的页面也能重新更新！把之前注入的统统去掉，重新插入
        if '<!-- INJECTED_NAV_TOC -->' in new_content:
            new_content = new_content.split('<!-- INJECTED_NAV_TOC -->')[0] + '</body>'

        # 注入的 HTML/JS/CSS（已移除对国内访问较慢的外部字体链接，使用系统原生字体栈即刻渲染）
        injected_html = """
<!-- INJECTED_NAV_TOC -->
<!-- 引入分包按需加载的思源宋体 (Noto Serif SC) -->
<link href="https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* 覆盖 Markdown 默认字体，仅在本地思源宋体和分包在线字体中选择 */
body, .markdown-preview.markdown-preview, .markdown-preview {
    font-size: 20px;
    line-height: 1.6;
    font-family: "Source Han Serif SC VF Regular", "Noto Serif SC", serif;
    font-weight: 500; /* 全局统一使用 Medium 字重 */
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 悬浮导航与目录样式 */
.custom-floating-nav {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 280px;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 15px;
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
.custom-floating-nav.minimized {
    width: 48px;
    height: 48px;
    min-height: 48px;
    border-radius: 50%;
    padding: 0;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.custom-floating-nav.minimized > *:not(.nav-minimize-btn) {
    display: none !important;
}
.custom-floating-nav .nav-minimize-btn {
    position: absolute;
    top: 15px;
    right: 15px;
    background: transparent;
    border: none;
    font-size: 14px;
    cursor: pointer;
    color: #888;
    padding: 4px;
    line-height: 1;
    border-radius: 4px;
}
.custom-floating-nav .nav-minimize-btn:hover {
    color: #333;
    background: #f0f0f0;
}
.custom-floating-nav.minimized .nav-minimize-btn {
    position: static;
    font-size: 24px;
    color: #228ae6;
    background: transparent;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
.custom-floating-nav .nav-btns {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    width: 100%;
}
.custom-floating-nav .home-btn, .custom-floating-nav .about-btn, .custom-floating-nav .category-btn {
    flex: 1;
    background: #228ae6;
    color: #fff;
    padding: 8px 10px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    transition: background 0.2s;
    box-sizing: border-box;
}
.custom-floating-nav .home-btn:hover { background: #1b6ec2; }
.custom-floating-nav .category-btn { background: #f06595; }
.custom-floating-nav .category-btn:hover { background: #d6336c; }
.custom-floating-nav .about-btn { background: #40c057; }
.custom-floating-nav .about-btn:hover { background: #2f9e44; }
.custom-floating-nav h3 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 5px;
}
.custom-floating-nav ul {
    list-style: none;
    padding-left: 15px;
    margin: 0;
}
.custom-floating-nav > ul {
    padding-left: 0;
}
.custom-floating-nav a.toc-link {
    text-decoration: none;
    color: #555;
    display: block;
    padding: 4px 0;
    font-size: 14px;
    line-height: 1.4;
    transition: color 0.2s;
}
.custom-floating-nav a.toc-link:hover {
    color: #228ae6;
}
/* 响应式，小屏幕下隐藏较长的目录，将返回主页变成底部悬浮按钮 */
@media (max-width: 1200px) {
    .custom-floating-nav.minimized {
        bottom: 30px;
        right: 20px;
        top: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        background: #ffffff;
        border: 1px solid #e0e0e0;
    }
    .custom-floating-nav {
        top: auto;
        bottom: 30px;
        right: 20px;
        width: auto;
        padding: 0;
        border: none;
        box-shadow: none;
        background: transparent;
    }
    .custom-floating-nav h3,
    .custom-floating-nav ul,
    .custom-floating-nav p {
        display: none; /* 手机上隐藏目录主体 */
    }
    .custom-floating-nav .nav-btns {
        margin-bottom: 0;
        width: auto;
    }
    .custom-floating-nav .home-btn, .custom-floating-nav .about-btn, .custom-floating-nav .category-btn {
        padding: 12px 20px;
        border-radius: 50px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        font-size: 16px;
    }
}
</style>
<script>
document.addEventListener("DOMContentLoaded", function() {
    if (document.querySelector('.custom-floating-nav')) return;
    
    const nav = document.createElement('div');
    nav.className = 'custom-floating-nav';
    
    // 最小化按钮
    const minBtn = document.createElement('button');
    minBtn.className = 'nav-minimize-btn';
    minBtn.innerHTML = '➖';
    minBtn.title = '收起目录';
    minBtn.onclick = function(e) {
        e.stopPropagation();
        if (nav.classList.contains('minimized')) {
            nav.classList.remove('minimized');
            minBtn.innerHTML = '➖';
            minBtn.title = '收起目录';
        } else {
            nav.classList.add('minimized');
            minBtn.innerHTML = '📑';
            minBtn.title = '展开目录';
        }
    };
    nav.onclick = function() {
        if (nav.classList.contains('minimized')) {
            nav.classList.remove('minimized');
            minBtn.innerHTML = '➖';
            minBtn.title = '收起目录';
        }
    };
    nav.appendChild(minBtn);

    // 导航按钮组
    const navGroup = document.createElement('div');
    navGroup.className = 'nav-btns';
    
    const homeBtn = document.createElement('a');
    homeBtn.href = '../index.html';
    homeBtn.className = 'home-btn';
    homeBtn.innerHTML = '🏠 首页';
    navGroup.appendChild(homeBtn);

    const categoryBtn = document.createElement('a');
    categoryBtn.href = '../category.html';
    categoryBtn.className = 'category-btn';
    categoryBtn.innerHTML = '🏷️ 分类';
    navGroup.appendChild(categoryBtn);

    const aboutBtn = document.createElement('a');
    aboutBtn.href = '../about.html';
    aboutBtn.className = 'about-btn';
    aboutBtn.innerHTML = 'ℹ️ 关于';
    navGroup.appendChild(aboutBtn);
    
    nav.appendChild(navGroup);
    
    // 目录标题
    const tocTitle = document.createElement('h3');
    tocTitle.innerText = '文章目录';
    nav.appendChild(tocTitle);
    
    // 生成目录
    const headers = document.querySelectorAll('h1, h2, h3');
    const ul = document.createElement('ul');
    headers.forEach((h, index) => {
        // 跳过主标题如果不希望它在目录里，这里全包含
        if (!h.id) h.id = 'heading-' + index;
        const li = document.createElement('li');
        // 根据标题级别缩进
        const level = parseInt(h.tagName[1]) - 1;
        li.style.marginLeft = (level * 15) + 'px';
        
        const a = document.createElement('a');
        a.href = '#' + h.id;
        a.className = 'toc-link';
        // 使用 innerHTML 使得数学公式（如 KaTeX 生成的 span）能在目录中正常渲染显示
        a.innerHTML = h.innerHTML;
        li.appendChild(a);
        ul.appendChild(li);
    });
    
    if (headers.length > 0) {
        nav.appendChild(ul);
    } else {
        const noToc = document.createElement('p');
        noToc.style.fontSize = '12px';
        noToc.style.color = '#999';
        noToc.textContent = '暂无目录';
        nav.appendChild(noToc);
    }
    
    document.body.appendChild(nav);
});
</script>

<!-- Giscus 评论区容器及资源引入 -->
<div style="max-width: 800px; margin: 0 auto; padding: 2rem; background: #fff; margin-top: 3rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <script src="https://giscus.app/client.js"
            data-repo="calculus1437/gitalk-comments"
            data-repo-id="R_kgDOSAPwtQ"
            data-category="Announcements"
            data-category-id="DIC_kwDOSAPwtc4C6vs6"
            data-mapping="pathname"
            data-strict="0"
            data-reactions-enabled="1"
            data-emit-metadata="0"
            data-input-position="top"
            data-theme="preferred_color_scheme"
            data-lang="zh-CN"
            crossorigin="anonymous"
            async>
    </script>
</div>

<footer style="text-align: center; margin-top: 5rem; padding: 1.5rem 0; color: #868e96; font-size: 0.9rem; border-top: 1px solid #eee; width: 100%;">
    Copyright 2026 HuangTianye 版权所有
</footer>
</body>"""

        # 替换 </body> 为 注入内容 + </body>
        new_content = new_content.replace('</body>', injected_html)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    except Exception as e:
        print(f"处理文件 {file_path} 添加侧边栏失败: {e}")

def get_html_title(file_path):
    """从 HTML 文件中提取 title 标签"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
    return os.path.basename(file_path).replace('.html', '')

def get_html_tags(file_path):
    """从 HTML 文件或文件名中提取标签"""
    tags = []
    # 1. 从文件名中提取 [Tag] 或 【Tag】
    filename = os.path.basename(file_path)
    match_brackets = re.findall(r'[\[【](.*?)[\]】]', filename)
    if match_brackets:
        tags.extend(match_brackets)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 2. 从 meta keywords 提取
            match_meta = re.search(r'<meta\s+name="keywords"\s+content="(.*?)">', content, re.IGNORECASE)
            if match_meta:
                keywords = [k.strip() for k in match_meta.group(1).split(',') if k.strip()]
                tags.extend(keywords)
            # 3. 从 HTML 注释提取 <!-- tags: tag1, tag2 -->
            match_comment = re.search(r'<!--\s*tags?:\s*(.*?)\s*-->', content, re.IGNORECASE)
            if match_comment:
                comment_tags = [k.strip() for k in match_comment.group(1).split(',') if k.strip()]
                tags.extend(comment_tags)
    except Exception as e:
        pass
        
    # 去重并过滤空值和 "默认分类" 以外的标签
    tags = list(set([t for t in tags if t]))
    if not tags:
        # 如果从文件名获取像 01_ 这样的也可以当作一种分类启发
        # 比如 "01_Understanding Analysis..." -> "Understanding Analysis"
        return ["默认分类"]
    return tags

def build_index():
    # 获取 posts 目录下的所有 html 文件
    post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html')]
    
    # 提取信息并生成列表
    posts_data = []
    for filename in post_files:
        file_path = os.path.join(POSTS_DIR, filename)
        title = get_html_title(file_path)
        tags = get_html_tags(file_path)
        # 获取文件的最后修改时间作为日期
        mtime = os.path.getmtime(file_path)
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

        posts_data.append({
            'filename': filename,
            'title': title,
            'date': date_str,
            'mtime': mtime,
            'tags': tags
        })

        # 为每篇文章处理增强（添加目录及返回主页按钮等）
        enhance_post(file_path)
    
    # 按文件名升序排序（保证第一章在前）
    posts_data.sort(key=lambda x: x['filename'])
    
    # 生成文章列表的 HTML
    lists_html = ""
    for post in posts_data:
        lists_html += f"""
            <li class="post-item">
                <span class="post-date">{post['date']}</span>
                <a class="post-link" href="{POSTS_DIR}/{post['filename']}">{post['title']}</a>
            </li>"""

    # 博客主页的 HTML 模板
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</title>
    <!-- 引入分包按需加载的思源宋体 (Noto Serif SC) -->
    <link href="https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --text-color: #333;
            --link-color: #228ae6;
            --link-hover: #1b6ec2;
            --date-color: #868e96;
            --border-color: #dee2e6;
        }}
        body {{
            /* 仅在本地思源宋体和分包在线字体中选择 */
            font-family: "Source Han Serif SC VF Regular", "Noto Serif SC", serif;
            font-weight: 500; /* 全局统一使用 Medium 字重 */
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-size: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border-color);
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #212529;
        }}
        .description {{
            color: var(--date-color);
            font-size: 1.1rem;
        }}
        .nav-links {{
            margin-top: 1rem;
        }}
        .nav-links a {{
            color: var(--link-color);
            text-decoration: none;
            margin: 0 10px;
            font-size: 1.1rem;
            font-weight: bold;
            transition: color 0.2s;
        }}
        .nav-links a:hover {{
            color: var(--link-hover);
        }}
        .post-list {{
            list-style: none;
            padding: 0;
        }}
        .post-item {{
            margin-bottom: 1.5rem;
            display: flex;
            align-items: baseline;
            gap: 1.5rem;
        }}
        .post-date {{
            color: var(--date-color);
            font-size: 0.9rem;
            min-width: 100px;
            font-family: monospace;
        }}
        .post-link {{
            color: var(--link-color);
            text-decoration: none;
            font-size: 1.25rem;
            font-weight: 500;
            transition: color 0.2s;
        }}
        .post-link:hover {{
            color: var(--link-hover);
            text-decoration: none;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 1rem;
            }}
            .post-item {{
                flex-direction: column;
                gap: 0.25rem;
                margin-bottom: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</h1>
        <p class="description">{SITE_CONFIG.get('description', '纯净的 HTML 数学笔记博客')}</p>
        <div class="nav-links">
            <a href="index.html">🏠 首页</a>
            <a href="category.html">🏷️ 分类</a>
            <a href="about.html">ℹ️ 关于</a>
        </div>
    </header>

    <main>
        <ul class="post-list">
            {lists_html if lists_html else "<li style='color: #868e96;'>暂无笔记，快去 posts 文件夹里放入导出的 HTML 吧！</li>"}
        </ul>
    </main>

    <footer style="text-align: center; margin-top: 3rem; padding: 1.5rem 0; color: #868e96; font-size: 0.9rem; border-top: 1px solid var(--border-color);">
        Copyright 2026 HuangTianye 版权所有
    </footer>
</body>
</html>"""

    # 写入 index.html
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    # 生成关于页面
    build_about()
    
    # 生成分类页面
    build_category(posts_data)

    print(f"✅ 博客主页、分类页面及关于页面构建成功！共识别到 {len(posts_data)} 篇笔记。")
    print(f"请使用浏览器打开 {os.path.abspath(INDEX_FILE)} 预览。")

def build_category(posts_data):
    # 按照标签构建分组
    tags_map = {}
    for post in posts_data:
        for tag in post.get('tags', ['未分类']):
            if tag not in tags_map:
                tags_map[tag] = []
            tags_map[tag].append(post)

    # 按包含文章数量降序、字母升序排列标签
    sorted_tags = sorted(tags_map.keys(), key=lambda t: (-len(tags_map[t]), t))

    # 生成 Tags pill 列表
    tags_pills_html = '<div class="tags-container">'
    for tag in sorted_tags:
        count = len(tags_map[tag])
        tags_pills_html += f'<a href="#{tag}" class="tag-pill"><span class="tag-name">{tag}</span><span class="tag-count">{count}</span></a>'
    tags_pills_html += '</div>'

    # 生成每个 Tag 下的文章列表
    tags_sections_html = ''
    for tag in sorted_tags:
        tags_sections_html += f'<h2 id="{tag}" class="category-title">{tag}</h2>'
        tags_sections_html += '<ul class="post-list">'
        for post in tags_map[tag]:
            tags_sections_html += f"""
                <li class="post-item">
                    <span class="post-date">{post['date']}</span>
                    <a class="post-link" href="{POSTS_DIR}/{post['filename']}">{post['title']}</a>
                </li>"""
        tags_sections_html += '</ul>'

    category_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>分类 - {SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</title>
    <!-- 引入分包按需加载的思源宋体 (Noto Serif SC) -->
    <link href="https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --text-color: #333;
            --link-color: #228ae6;
            --link-hover: #1b6ec2;
            --date-color: #868e96;
            --border-color: #dee2e6;
        }}
        body {{
            font-family: "Source Han Serif SC VF Regular", "Noto Serif SC", serif;
            font-weight: 500;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-size: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border-color);
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #212529;
        }}
        .description {{
            color: var(--date-color);
            font-size: 1.1rem;
        }}
        .nav-links {{
            margin-top: 1rem;
        }}
        .nav-links a {{
            color: var(--link-color);
            text-decoration: none;
            margin: 0 10px;
            font-size: 1.1rem;
            font-weight: bold;
            transition: color 0.2s;
        }}
        .nav-links a:hover {{
            color: var(--link-hover);
        }}
        .tags-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 3rem;
        }}
        .tag-pill {{
            display: inline-flex;
            align-items: center;
            text-decoration: none;
            background: #495057;
            color: #fff;
            border-radius: 4px;
            overflow: hidden;
            font-size: 0.95rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .tag-pill:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .tag-name {{
            padding: 4px 10px;
        }}
        .tag-count {{
            background: #868e96;
            padding: 4px 8px;
            font-size: 0.85rem;
        }}
        .category-title {{
            font-size: 2rem;
            margin-top: 3rem;
            margin-bottom: 1rem;
            color: #212529;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        .post-list {{
            list-style: none;
            padding: 0;
            margin-bottom: 2rem;
        }}
        .post-item {{
            margin-bottom: 0.8rem;
            display: flex;
            align-items: baseline;
            gap: 1rem;
        }}
        .post-date {{
            color: var(--date-color);
            font-size: 0.9rem;
            font-family: monospace;
            min-width: 95px;
        }}
        .post-link {{
            color: var(--text-color);
            text-decoration: none;
            font-size: 1.15rem;
            transition: color 0.2s;
        }}
        .post-link:hover {{
            color: var(--link-color);
            text-decoration: none;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            .post-item {{ flex-direction: column; gap: 0.25rem; margin-bottom: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</h1>
        <p class="description">{SITE_CONFIG.get('description', '纯净的 HTML 数学笔记博客')}</p>
        <div class="nav-links">
            <a href="index.html">🏠 首页</a>
            <a href="category.html">🏷️ 分类</a>
            <a href="about.html">ℹ️ 关于</a>
        </div>
    </header>

    <main>
        <h2 style="font-size: 2.5rem; margin-top: 0; margin-bottom: 1.5rem;">Tags</h2>
        {tags_pills_html}
        {tags_sections_html}
    </main>

    <footer style="text-align: center; margin-top: 4rem; padding: 1.5rem 0; color: #868e96; font-size: 0.9rem; border-top: 1px solid var(--border-color);">
        Copyright 2026 HuangTianye 版权所有
    </footer>
</body>
</html>"""
    with open('category.html', 'w', encoding='utf-8') as f:
        f.write(category_html)

def build_about():
    # 查找 readme.md (不区分大小写)
    readme_path = 'readme.md'
    for f in os.listdir('.'):
        if f.lower() == 'readme.md':
            readme_path = f
            break
            
    md_content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
    else:
        md_content = "# 关于\n\n你好！这里是 calculus_1437 的数学笔记博客系统。\n此页面由根目录下的 `readme.md` 自动生成，可以自由编辑更新内容。"
        with open('readme.md', 'w', encoding='utf-8') as f:
            f.write(md_content)

    md_json = json.dumps(md_content)

    about_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>关于 - {SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</title>
    <!-- 引入分包按需加载的思源宋体 (Noto Serif SC) -->
    <link href="https://fonts.loli.net/css2?family=Noto+Serif+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <!-- KaTeX 支持 (解决公式渲染) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css">
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --text-color: #333;
            --link-color: #228ae6;
            --link-hover: #1b6ec2;
            --date-color: #868e96;
            --border-color: #dee2e6;
        }}
        body {{
            /* 仅在本地思源宋体和分包在线字体中选择 */
            font-family: "Source Han Serif SC VF Regular", "Noto Serif SC", serif;
            font-weight: 500; /* 全局统一使用 Medium 字重 */
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            font-size: 20px;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border-color);
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            color: #212529;
        }}
        .description {{
            color: var(--date-color);
            font-size: 1.1rem;
        }}
        .nav-links {{
            margin-top: 1rem;
        }}
        .nav-links a {{
            color: var(--link-color);
            text-decoration: none;
            margin: 0 10px;
            font-size: 1.1rem;
            font-weight: bold;
            transition: color 0.2s;
        }}
        .nav-links a:hover {{
            color: var(--link-hover);
        }}
        .content {{
            background: #fff;
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        /* Markdown 常用样式 */
        .content h1, .content h2, .content h3 {{ color: #222; border-bottom: 1px solid #eee; padding-bottom: 0.5rem; }}
        .content a {{ color: var(--link-color); text-decoration: none; }}
        .content blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 1rem; color: #666; }}
        .content code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
        .content pre {{ background: #f4f4f4; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        .content img {{ max-width: 100%; height: auto; }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            .content {{ padding: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{SITE_CONFIG.get('title', 'calculus_1437''s Math Notes')}</h1>
        <p class="description">{SITE_CONFIG.get('description', '纯净的 HTML 数学笔记博客')}</p>
        <div class="nav-links">
            <a href="index.html">🏠 首页</a>
            <a href="category.html">🏷️ 分类</a>
            <a href="about.html">ℹ️ 关于</a>
        </div>
    </header>

    <main>
        <div class="content" id="md-content">
            加载中... (正在联网获取 marked.js 解析引擎)
        </div>
    </main>

    <footer style="text-align: center; margin-top: 3rem; padding: 1.5rem 0; color: #868e96; font-size: 0.9rem; border-top: 1px solid var(--border-color);">
        Copyright 2026 HuangTianye 版权所有
    </footer>

    <!-- 纯前端渲染 Markdown 方案引入 -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.js"></script>
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/contrib/auto-render.min.js"></script>
    
    <script>
        // 把 Markdown 源文件内容作为一个安全的 JSON 字符串传入
        const rawMd = {md_json};
        
        document.addEventListener("DOMContentLoaded", function() {{
            // 解析 Markdown
            document.getElementById('md-content').innerHTML = marked.parse(rawMd);
            
            // 渲染数学公式 KaTeX
            if (window.renderMathInElement) {{
                renderMathInElement(document.getElementById('md-content'), {{
                    delimiters: [
                        {{left: "$$", right: "$$", display: true}},
                        {{left: "$", right: "$", display: false}}
                    ],
                    throwOnError : false
                }});
            }}
        }});
    </script>
</body>
</html>"""
    with open('about.html', 'w', encoding='utf-8') as f:
        f.write(about_html)

if __name__ == '__main__':
    build_index()
