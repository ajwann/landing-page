// Google Analytics bootstrap, kept out of index.html so the
// Content-Security-Policy needs no 'unsafe-inline'.
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());

gtag('config', 'G-5CHWXMVCVD');

// Name of the <details> section an element sits in, from its <summary> heading.
function sectionName(el) {
    var h2 = el && el.closest('details.link-group') && el.closest('details.link-group').querySelector('summary h2');
    return h2 ? h2.textContent.trim() : '';
}

// Which sections get expanded or collapsed. 'toggle' doesn't bubble, so listen in the capture phase.
document.addEventListener('toggle', function (e) {
    if (!(e.target instanceof Element) || !e.target.matches('details.link-group')) return;
    gtag('event', 'section_toggle', {
        section: sectionName(e.target),
        state: e.target.open ? 'open' : 'close'
    });
}, true);

// Which links get clicked, including mailto: links that GA's outbound tracking skips.
document.addEventListener('click', function (e) {
    var a = e.target instanceof Element && e.target.closest('.link-list a[href]');
    if (!a) return;
    var badge = a.querySelector('.badge');
    var text = a.textContent;
    if (badge) text = text.replace(badge.textContent, '');
    gtag('event', 'link_click', {
        link_url: a.href,
        link_text: text.trim(),
        section: sectionName(a),
        transport_type: 'beacon'
    });
});
