// Preserve bookmarked section links while consolidating the legacy pages.
(() => {
    const target = document.body.dataset.redirect;
    if (!target) return;
    const destination = new URL(target, window.location.href);
    if (destination.origin !== window.location.origin) return;
    const legacyServices = {
        "#incidentes": "#incident",
        "#automacoes": "#automation",
        "#ferramentas": "#tools",
        "#integracoes": "#integration",
        "#contato": "#contact",
        "#topo": "#top"
    };
    if (window.location.pathname.endsWith("/servicos.html")) {
        destination.hash = legacyServices[window.location.hash] || "#services";
    } else if (window.location.hash) {
        destination.hash = window.location.hash === "#ferramentas" ? "#lab" : window.location.hash;
    }
    window.location.replace(destination.href);
})();
