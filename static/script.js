// 树状导航展开/折叠功能
document.querySelectorAll('.sidebar.tree-nav > li > span').forEach(item => {
    item.addEventListener('click', () => {
        const subMenu = item.nextElementSibling;
        console.log(item);
        if (subMenu) {
            subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
        }
    });
});
