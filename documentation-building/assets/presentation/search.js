/* Adapted from the LD local search; no project paths or teaching data. */
(() => {
  const normalize = value => String(value).normalize('NFKC').toLowerCase();
  const words = value => normalize(value).match(/[\p{L}\p{N}_]+/gu) || [];
  function distance(a, b) {
    let row = Array.from({length: b.length + 1}, (_, i) => i);
    for (let i = 0; i < a.length; i++) {
      const next = [i + 1];
      for (let j = 0; j < b.length; j++) next[j + 1] = Math.min(next[j] + 1, row[j + 1] + 1, row[j] + (a[i] === b[j] ? 0 : 1));
      row = next;
    }
    return row[b.length];
  }
  function searchSlides(records, query, {includeNotes = false} = {}) {
    const terms = words(query);
    if (!terms.length) return [];
    return records.flatMap(record => {
      const title = normalize(record.title), text = normalize(record.visible_text || '');
      const notes = includeNotes ? normalize(record.approved_notes || '') : '';
      const titleWords = words(title), bodyWords = words(text + ' ' + notes);
      let score = 0;
      for (const term of terms) {
        const cjk = /[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u.test(term);
        if (titleWords.includes(term) || (cjk && title.includes(term))) { score += 12; continue; }
        if (bodyWords.includes(term) || (cjk && (text.includes(term) || notes.includes(term)))) { score += 8; continue; }
        if ([...titleWords, ...bodyWords].some(w => w.startsWith(term))) { score += 5; continue; }
        // Fuzzy matching is for alphabetic spelling, never numeric identifiers.
        const tolerance = /^[a-z]{4,}$/.test(term) ? (term.length >= 7 ? 2 : 1) : 0;
        if (tolerance && [...titleWords, ...bodyWords].some(w => Math.abs(w.length - term.length) <= tolerance && distance(w, term) <= tolerance)) score++;
        else return [];
      }
      return [{...record, score}];
    }).sort((a, b) => b.score - a.score || a.index - b.index);
  }
  globalThis.DocumentationSearch = {searchSlides};
})();
