// Enhance the static navigation; links remain available when JavaScript is disabled.
(() => {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector("#site-navigation");
    if (toggle && nav) {
        const mobile = window.matchMedia("(max-width: 70rem)");
        const label = toggle.querySelector("[data-menu-label]");
        const setOpen = (open) => {
            toggle.setAttribute("aria-expanded", String(open));
            toggle.setAttribute("aria-label", open ? "Fechar menu de navegação" : "Abrir menu de navegação");
            if (label) label.textContent = open ? "Fechar" : "Menu";
            nav.hidden = mobile.matches && !open;
        };
        const syncViewport = () => {
            // Do not leave focus in a navigation region that is about to be hidden.
            if (mobile.matches && nav.contains(document.activeElement)) toggle.focus();
            if (!mobile.matches && document.activeElement === toggle) nav.querySelector("a")?.focus();
            setOpen(false);
        };
        toggle.hidden = false;
        toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && mobile.matches && toggle.getAttribute("aria-expanded") === "true") {
                setOpen(false);
                toggle.focus();
            }
        });
        document.addEventListener("click", (event) => {
            if (mobile.matches && !nav.hidden && !nav.contains(event.target) && !toggle.contains(event.target)) setOpen(false);
        });
        nav.addEventListener("click", (event) => {
            if (event.target.closest("a") && mobile.matches) {
                setOpen(false);
                toggle.focus();
            }
        });
        mobile.addEventListener("change", syncViewport);
        syncViewport();
    }

    // Keep preview visits out of production analytics.
    if (["gsasec.com.br", "www.gsasec.com.br"].includes(window.location.hostname)) {
        window.dataLayer = window.dataLayer || [];
        window.gtag = function () { window.dataLayer.push(arguments); };
        window.gtag("js", new Date());
        window.gtag("config", "G-WGSJJ6R80P");
        const script = document.createElement("script");
        script.async = true;
        script.src = "https://www.googletagmanager.com/gtag/js?id=G-WGSJJ6R80P";
        document.head.appendChild(script);
    }
})();
