/* Fix fragment anchor scrolling for Material's instant navigation.
 * Material intercepts #fragment link clicks and updates the URL but does not
 * always scroll to the target — especially for <span id> anchors that are not
 * headings. This listener queues a scroll after Material's synchronous handling.
 */
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[href^="#"]');
  if (!a) return;
  const id = decodeURIComponent(a.getAttribute('href').slice(1));
  if (!id) return;
  const el = document.getElementById(id);
  if (!el) return;
  setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0);
});

/* Handle SVG <a data-href> navigation.
 * SVG <a> elements (SVGAElement) have a read-only .href property, so Material's
 * instant navigation crashes trying to set it.  We strip href → data-href in
 * hooks.py for all SVG <a> elements (vacuum diagrams, image annotator hit paths)
 * and handle clicks here instead.
 */
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[data-href]');
  if (!a) return;
  e.preventDefault();
  const href = a.getAttribute('data-href');
  if (!href) return;
  if (href.startsWith('#')) {
    const id = decodeURIComponent(href.slice(1));
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } else {
    window.location.href = href;
  }
});
