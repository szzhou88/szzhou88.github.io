'use strict';
const papers = [...document.querySelectorAll('.publication')];
const search = document.querySelector('#paper-search');
const resultCount = document.querySelector('#result-count');
const emptyState = document.querySelector('#empty-state');

function updatePublications() {
  const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  let count = 0;
  papers.forEach(paper => {
    const searchable = paper.querySelector('.paper-main').textContent.toLocaleLowerCase();
    const visible = terms.every(term => searchable.includes(term));
    paper.hidden = !visible;
    if (visible) count += 1;
  });
  resultCount.textContent = `${count} ${count === 1 ? 'publication' : 'publications'}`;
  emptyState.hidden = count > 0;
}

search.addEventListener('input', updatePublications);
document.querySelector('#reset-search').addEventListener('click', () => {
  search.value = '';
  updatePublications();
  search.focus();
});
document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
    event.preventDefault();
    search.focus();
  }
  if (event.key === 'Escape' && document.activeElement === search) {
    search.value = '';
    updatePublications();
  }
});
document.querySelector('.publication-toolbar').hidden = false;

const links = [...document.querySelectorAll('.nav-link')];
const sections = links.map(link => document.querySelector(link.getAttribute('href')));
let scrollQueued = false;
function updateNavigation() {
  let current = sections[0];
  sections.forEach(section => { if (section.getBoundingClientRect().top <= 150) current = section; });
  links.forEach(link => {
    const active = link.getAttribute('href') === `#${current.id}`;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  scrollQueued = false;
}
window.addEventListener('scroll', () => {
  if (!scrollQueued) { scrollQueued = true; requestAnimationFrame(updateNavigation); }
}, {passive: true});
updateNavigation();
