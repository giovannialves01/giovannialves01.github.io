document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll('a[href="#"]');

    links.forEach(link => {
        // Evita aplicar duas vezes
        if (link.dataset.disabled) return;

        // Guarda o texto original (opcional, útil no futuro)
        const originalText = link.textContent.trim();

        // Altera o texto do link
        link.textContent = `${originalText} — ainda não disponível`;

        // Estilo visual
        link.style.color = "red";
        link.style.cursor = "not-allowed";
        link.style.pointerEvents = "none"; // bloqueia clique de vez
        link.style.textDecoration = "none";
        link.style.opacity = "0.85";

        // Marca como processado
        link.dataset.disabled = "true";
    });
});
