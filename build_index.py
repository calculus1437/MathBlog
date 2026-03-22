import os
import re
from datetime import datetime

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
<style>
/* 覆盖 Markdown 默认字体，配置为你要求的全局字体， fallback 到各类系统的流畅字体 */
body, .markdown-preview.markdown-preview, .markdown-preview {
    font-size: 20px;
    line-height: 1.6;
    font-family: "Source Han Serif SC VF Regular", "Source Han Serif SC", "Noto Serif CJK SC", "PingFang SC", "Microsoft YaHei", serif;
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
.custom-floating-nav .home-btn {
    display: inline-block;
    background: #228ae6;
    color: #fff;
    padding: 8px 12px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 14px;
    margin-bottom: 15px;
    font-weight: bold;
    text-align: center;
    width: calc(100% - 24px);
    transition: background 0.2s;
}
.custom-floating-nav .home-btn:hover {
    background: #1b6ec2;
}
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
/* 响应式，小屏幕隐藏或变成按钮 */
@media (max-width: 1200px) {
    .custom-floating-nav {
        display: none;
    }
}
</style>
<script>
document.addEventListener("DOMContentLoaded", function() {
    if (document.querySelector('.custom-floating-nav')) return;
    
    const nav = document.createElement('div');
    nav.className = 'custom-floating-nav';
    
    // 返回主页按钮
    const homeBtn = document.createElement('a');
    homeBtn.href = '../index.html';
    homeBtn.className = 'home-btn';
    homeBtn.innerHTML = '← 返回主页';
    nav.appendChild(homeBtn);
    
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
        a.textContent = h.textContent;
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

def build_index():
    # 获取 posts 目录下的所有 html 文件
    post_files = [f for f in os.listdir(POSTS_DIR) if f.endswith('.html')]
    
    # 提取信息并生成列表
    posts_data = []
    for filename in post_files:
        file_path = os.path.join(POSTS_DIR, filename)
        title = get_html_title(file_path)
        # 获取文件的最后修改时间作为日期
        mtime = os.path.getmtime(file_path)
        date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        
        posts_data.append({
            'filename': filename,
            'title': title,
            'date': date_str,
            'mtime': mtime
        })
        
        # 为每篇文章处理增强（添加目录及返回主页按钮）
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
    <title>Calculus's Math Notes</title>
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
            /* 移除了庞大的在线字体，采用系统自带流畅字体链，保障手机端秒开 */
            font-family: "Source Han Serif SC VF Regular", "Source Han Serif SC", "Noto Serif CJK SC", "PingFang SC", "Microsoft YaHei", serif;
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
            text-decoration: underline;
        }}
        @media (max-width: 600px) {{
            .post-item {{
                flex-direction: column;
                gap: 0.25rem;
                margin-bottom: 2rem;
            }}
            body {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Calculus's Math Notes</h1>
        <p class="description">纯净的 HTML 数学笔记博客</p>
    </header>
    
    <main>
        <ul class="post-list">
            {lists_html if lists_html else "<li style='color: #868e96;'>暂无笔记，快去 posts 文件夹里放入导出的 HTML 吧！</li>"}
        </ul>
    </main>
</body>
</html>"""

    # 写入 index.html
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ 博客主页构建成功！共识别到 {len(posts_data)} 篇笔记。")
    print(f"请使用浏览器打开 {os.path.abspath(INDEX_FILE)} 预览。")

if __name__ == '__main__':
    build_index()
