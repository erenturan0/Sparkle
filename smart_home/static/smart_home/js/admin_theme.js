(function () {
    const html = document.documentElement;

    function isLight() {
        return localStorage.getItem('sparkle-theme') === 'light' || localStorage.getItem('jazzmin-theme-mode') === 'light';
    }

    function applyTheme() {
        const mode = isLight() ? 'light' : 'dark';
        html.setAttribute('data-bs-theme', mode);
        localStorage.setItem('jazzmin-theme-mode', mode);
        updateIcon();
    }

    function updateIcon() {
        const btn = document.getElementById('sparkle-theme-toggle');
        if (!btn) return;
        const icon = btn.querySelector('i');
        if (icon) {
            icon.className = isLight() ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    function toggleTheme(e) {
        if (e) e.preventDefault();
        const next = isLight() ? 'dark' : 'light';
        localStorage.setItem('sparkle-theme', next);
        localStorage.setItem('jazzmin-theme-mode', next);
        applyTheme();
    }

    applyTheme();

    document.addEventListener('DOMContentLoaded', function () {
        const navRight = document.querySelector('.navbar-nav.ms-auto') ||
            document.querySelector('.navbar-nav.ml-auto') ||
            document.querySelector('.main-header .navbar-nav:last-of-type');

        if (navRight) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.innerHTML = `
                <a class="nav-link" href="#" id="sparkle-theme-toggle" role="button" title="Tema Değiştir">
                    <i class="fas fa-sun"></i>
                </a>
            `;
            navRight.appendChild(li);

            document.getElementById('sparkle-theme-toggle').addEventListener('click', toggleTheme);
            updateIcon();
        }
    });

    window.addEventListener('storage', function (e) {
        if (e.key === 'sparkle-theme' || e.key === 'jazzmin-theme-mode') {
            applyTheme();
        }
    });
})();
