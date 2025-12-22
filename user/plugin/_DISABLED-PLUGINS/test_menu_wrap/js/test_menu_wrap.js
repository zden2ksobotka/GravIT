document.addEventListener('DOMContentLoaded', () => {
    const hasSubmenus = document.querySelectorAll('.has-submenu');
    let hideTimeout;

    // Add a class to the body to indicate JS is active and can control dropdowns
    document.body.classList.add('js-active-dropdowns');

    hasSubmenus.forEach(item => {
        const submenu = item.querySelector('.submenu');
        if (!submenu) return;

        item.addEventListener('mouseenter', () => {
            clearTimeout(hideTimeout);
            submenu.classList.add('submenu-open');
        });

        item.addEventListener('mouseleave', () => {
            hideTimeout = setTimeout(() => {
                submenu.classList.remove('submenu-open');
            }, 200); // Delay hiding by 200ms
        });

        // Keep submenu open if mouse enters the submenu itself
        submenu.addEventListener('mouseenter', () => {
            clearTimeout(hideTimeout);
        });

        submenu.addEventListener('mouseleave', () => {
            hideTimeout = setTimeout(() => {
                submenu.classList.remove('submenu-open');
            }, 200); // Delay hiding by 200ms
        });
    });
});
