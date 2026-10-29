import {test} from 'node:test';
import assert from 'node:assert/strict';
import '../documentation-building/assets/presentation/search.js';
const {searchSlides} = globalThis.DocumentationSearch;
const records = [
  {index: 0, title: '如何辨識對話交錯', visible_text: '檢查來源先後次序。', approved_notes: 'ApprovedNoteKeyword'},
  {index: 1, title: 'Password changes', visible_text: 'Review settings.', approved_notes: ''},
  {index: 2, title: 'Settings', visible_text: 'Password changes are available.', approved_notes: ''},
  {index: 3, title: 'Ship 398', visible_text: 'Use channel 67.', approved_notes: ''}
];
test('Chinese middle substring matches', () => assert.equal(searchSlides(records, '對話')[0].index, 0));
test('visible text matches with multiple terms', () => assert.equal(searchSlides(records, '來源 次序')[0].index, 0));
test('title ranks before body', () => assert.deepEqual(searchSlides(records, 'password').map(x => x.index), [1, 2]));
test('approved notes require opt-in', () => {
  assert.equal(searchSlides(records, 'ApprovedNoteKeyword').length, 0);
  assert.equal(searchSlides(records, 'ApprovedNoteKeyword', {includeNotes: true}).length, 1);
});
test('English typo matching', () => assert.equal(searchSlides(records, 'passwrod')[0].index, 1));
test('full-width normalized', () => assert.equal(searchSlides(records, '３９８')[0].index, 3));
test('numeric identifiers do not receive fuzzy matching', () => assert.equal(searchSlides(records, '399').length, 0));
test('empty and absent queries yield no results', () => { assert.equal(searchSlides(records, '').length, 0); assert.equal(searchSlides(records, 'zzzzzzzz').length, 0); });
