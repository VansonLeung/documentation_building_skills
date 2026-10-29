/* Behavior only; teaching content stays in the maintained HTML. */
(() => {
  const slides = [...document.querySelectorAll('section.slide')];
  const zh = document.documentElement.lang === 'zh-Hant', say = (en, cn) => zh ? cn : en;
  const exporting = new URLSearchParams(location.search).has('export');
  if (exporting) document.body.classList.add('export-mode');
  slides.forEach((s, i) => { s.querySelector('[data-number]').textContent = `${i + 1} / ${slides.length}`; });
  window.documentationReady = (async () => {
    if (!exporting) {
      await Reveal.initialize({width: 1280, height: 720, center: false, margin: .025, hash: true,
        transition: 'none', keyboard: {191: null}, pdfSeparateFragments: false, scrollActivationWidth: null});
      const stopMedia = () => document.querySelectorAll('audio,video').forEach(a => a.pause());
      Reveal.on('slidechanged', stopMedia);
      const toggle = document.querySelector('[data-reading]');
      function setReading(enabled, index) {
        stopMedia(); Reveal.toggleOverview(false); Reveal.togglePause(false);
        document.body.classList.toggle('reading', enabled);
        toggle.textContent = enabled ? say('Presentation view', '演講模式') : say('Reading view', '閱讀模式');
        toggle.setAttribute('aria-pressed', String(enabled));
        Reveal.configure({keyboard: enabled ? false : {191: null}});
        if (enabled) requestAnimationFrame(() => slides[index].scrollIntoView({block: 'start'}));
        else { window.scrollTo(0, 0); Reveal.slide(index); Reveal.layout(); document.querySelector('.reveal').focus({preventScroll: true}); }
      }
      document.querySelector('.reveal').tabIndex = -1;
      toggle.addEventListener('click', () => {
        const reading = document.body.classList.contains('reading');
        const index = reading ? slides.reduce((best, s, i) => Math.abs(s.getBoundingClientRect().top - 60) < Math.abs(slides[best].getBoundingClientRect().top - 60) ? i : best, 0) : Reveal.getIndices().h;
        setReading(!reading, index);
      });
      slides.forEach((slide, i) => {
        const button = document.createElement('button'); button.className = 'present-slide'; button.type = 'button';
        button.textContent = say('Present this slide', '播放此頁');
        button.addEventListener('click', () => setReading(false, i)); slide.querySelector('footer').append(button);
      });
      document.querySelector('[data-language]').addEventListener('click', event => {
        stopMedia(); const a = event.currentTarget;
        const current = document.body.classList.contains('reading') ? slides.reduce((best, s, i) => Math.abs(s.getBoundingClientRect().top - 60) < Math.abs(slides[best].getBoundingClientRect().top - 60) ? i : best, 0) : Reveal.getIndices().h;
        a.hash = '/' + slides[current].id;
      });
      const records = slides.map((s, i) => ({id: s.id, index: i, title: s.querySelector('h1,h2').textContent,
        visible_text: s.querySelector('.slide-content').innerText,
        approved_notes: [...s.querySelectorAll('.notes[data-share="approved"]')].map(n => n.textContent).join(' ')}));
      const dialog = document.createElement('dialog'); dialog.className = 'search-dialog';
      dialog.setAttribute('aria-labelledby', 'search-title');
      dialog.innerHTML = `<header><h2 id="search-title">${say('Search slides', '搜尋簡報')}</h2><button data-close>${say('Close', '關閉')}</button></header><label>${say('Keywords', '關鍵詞')}<input type="search" data-query></label><label><input type="checkbox" data-notes> ${say('Include approved speaker notes', '包括已批准的講者備註')}</label><p data-count role="status" aria-live="polite"></p><ol data-results></ol>`;
      document.body.append(dialog);
      const query = dialog.querySelector('[data-query]'), notes = dialog.querySelector('[data-notes]');
      function render() {
        const hits = DocumentationSearch.searchSlides(records, query.value, {includeNotes: notes.checked});
        dialog.querySelector('[data-count]').textContent = !query.value.trim() ? say('Enter keywords. Screenshot text is not indexed.', '輸入關鍵詞，截圖內文字未納入搜尋。') : `${hits.length} ${say('matching slides', '張相符投影片')}`;
        const list = dialog.querySelector('[data-results]'); list.replaceChildren();
        for (const hit of hits.slice(0, 20)) {
          const li = document.createElement('li'), button = document.createElement('button'); button.type = 'button';
          button.textContent = `${hit.index + 1}. ${hit.title}`;
          button.addEventListener('click', () => { dialog.close(); if (document.body.classList.contains('reading')) slides[hit.index].scrollIntoView({block: 'start'}); else Reveal.slide(hit.index); });
          li.append(button); list.append(li);
        }
      }
      const trigger = document.querySelector('[data-search]');
      const open = () => { if (!dialog.open) { render(); dialog.showModal(); query.focus(); } };
      trigger.addEventListener('click', open); query.addEventListener('input', render); notes.addEventListener('change', render);
      dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
      dialog.addEventListener('close', () => trigger.focus({preventScroll: true}));
      dialog.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Escape') { e.preventDefault(); dialog.close(); } if (e.key === 'Enter' && e.target === query) { e.preventDefault(); dialog.querySelector('[data-results] button')?.click(); } });
      document.addEventListener('keydown', e => {
        if (dialog.open || e.target.closest('input,textarea,select,[contenteditable="true"]')) return;
        if (e.key === '/' || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) { e.preventDefault(); e.stopImmediatePropagation(); open(); }
      }, true);
    }
    await document.fonts.ready;
    await Promise.all([...document.images].map(img => img.decode()));
    return {slides: slides.length, exporting};
  })();
})();
