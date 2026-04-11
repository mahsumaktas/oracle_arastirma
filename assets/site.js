(function () {
  var root = document.documentElement;
  var storageKey = 'oracle-research-theme';
  function applyTheme(theme) {
    if (theme === 'light') root.setAttribute('data-theme', 'light');
    else if (theme === 'dark') root.setAttribute('data-theme', 'dark');
    else root.removeAttribute('data-theme');
    var icon = document.querySelector('[data-theme-icon]');
    if (icon) {
      icon.textContent = theme === 'light' ? '☀' : theme === 'dark' ? '☾' : '◐';
    }
  }
  applyTheme(localStorage.getItem(storageKey) || 'auto');
  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-theme-toggle]');
    if (!target) return;
    var current = localStorage.getItem(storageKey) || 'auto';
    var next = current === 'auto' ? 'dark' : current === 'dark' ? 'light' : 'auto';
    localStorage.setItem(storageKey, next);
    applyTheme(next);
  });

  var search = document.querySelector('[data-report-search]');
  if (search) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-report-card]'));
    var empty = document.querySelector('[data-search-empty]');
    var runSearch = function () {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var haystack = (card.getAttribute('data-search') || '').toLowerCase();
        var show = !query || haystack.indexOf(query) !== -1;
        card.style.display = show ? '' : 'none';
        if (show) visible += 1;
      });
      if (empty) empty.classList.toggle('is-visible', visible === 0);
    };
    search.addEventListener('input', runSearch);
    runSearch();
  }

  var topBtn = document.querySelector('[data-back-top]');
  if (topBtn) {
    var onScroll = function () {
      topBtn.classList.toggle('is-visible', window.scrollY > 420);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    topBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  var reportPayload = document.getElementById('report-data');
  if (reportPayload && window.marked) {
    var data = JSON.parse(reportPayload.textContent);
    var container = document.querySelector('[data-report-sections]');
    if (container) {
      marked.setOptions({ gfm: true, breaks: false, mangle: false, headerIds: false });
      var renderer = new marked.Renderer();
      renderer.table = function (header, body) {
        return '<div class="table-wrap"><table><thead>' + header + '</thead><tbody>' + body + '</tbody></table></div>';
      };
      container.innerHTML = data.sections.map(function (section, index) {
        return [
          '<section class="report-section" id="' + section.id + '">',
          '<div class="section-head">',
          '<div>',
          '<div class="section-kicker">' + data.sectionLabel + ' ' + String(index + 1).padStart(2, '0') + '</div>',
          '<h2>' + escapeHtml(section.title) + '</h2>',
          '</div>',
          '<a class="ghost-button" href="#' + section.id + '">#</a>',
          '</div>',
          '<div class="rendered-markdown">' + marked.parse(section.content, { renderer: renderer }) + '</div>',
          '</section>'
        ].join('');
      }).join('');
    }

    var sectionLinks = Array.prototype.slice.call(document.querySelectorAll('[data-section-link]'));
    if (sectionLinks.length) {
      var ids = sectionLinks.map(function (link) { return link.getAttribute('href').replace('#', ''); });
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var id = entry.target.getAttribute('id');
          sectionLinks.forEach(function (link) {
            link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
          });
        });
      }, { rootMargin: '-30% 0px -55% 0px', threshold: 0 });
      ids.forEach(function (id) {
        var node = document.getElementById(id);
        if (node) observer.observe(node);
      });
    }
  }

  function escapeHtml(input) {
    return String(input)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
})();
