// toc.js - 自动生成悬浮目录树，只保留一个返回首页的按钮
(function() {
    if (document.querySelector('.custom-floating-nav')) return;

    const nav = document.createElement('div');
    nav.className = 'custom-floating-nav';

    // 最小化按钮
    const minBtn = document.createElement('button');
    minBtn.className = 'nav-minimize-btn';
    minBtn.innerHTML = '➖';
    minBtn.title = '收起目录';
    minBtn.onclick = (e) => {
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
    nav.appendChild(minBtn);

    // 导航按钮组：只保留首页按钮
    const navGroup = document.createElement('div');
    navGroup.className = 'nav-btns';
    const homeBtn = document.createElement('a');
    homeBtn.href = '../index.html';
    homeBtn.className = 'home-btn';
    homeBtn.innerHTML = '🏠 首页';
    navGroup.appendChild(homeBtn);
    nav.appendChild(navGroup);

    // 目录标题
    const tocTitle = document.createElement('h3');
    tocTitle.innerText = '文章目录';
    nav.appendChild(tocTitle);

    // 生成目录（h1, h2, h3）
    const headers = document.querySelectorAll('h1, h2, h3');
    if (headers.length === 0) {
        const noToc = document.createElement('p');
        noToc.style.fontSize = '12px';
        noToc.style.color = '#999';
        noToc.textContent = '暂无目录';
        nav.appendChild(noToc);
    } else {
        const ul = document.createElement('ul');
        headers.forEach((h, idx) => {
            if (!h.id) h.id = `heading-${idx}`;
            const li = document.createElement('li');
            const level = parseInt(h.tagName[1]) - 1;
            li.style.marginLeft = `${level * 15}px`;
            const a = document.createElement('a');
            a.href = `#${h.id}`;
            a.className = 'toc-link';
            a.innerHTML = h.innerHTML; // 保留子元素（如数学公式）
            li.appendChild(a);
            ul.appendChild(li);
        });
        nav.appendChild(ul);
    }

    document.body.appendChild(nav);
})();