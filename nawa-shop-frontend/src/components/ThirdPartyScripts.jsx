import { useEffect } from "react";

/**
 * Injecte dynamiquement les scripts tiers (GA, FB Pixel, Crisp, etc.)
 * définis dans l'admin Django.
 */
export default function ThirdPartyScripts() {
  useEffect(() => {
    fetch("/api/v1/third-party-scripts/")
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        list.forEach((script) => injectScript(script));
      })
      .catch((err) => console.warn("Scripts tiers indisponibles:", err));
  }, []);

  return null;
}

function injectScript(script) {
  const { code, location, name, id } = script;

  // Anti-doublon
  if (document.querySelector(`[data-cms-script="${id || name}"]`)) return;

  const container = document.createElement("div");
  container.setAttribute("data-cms-script", id || name);
  container.innerHTML = code;

  // Ré-exécuter les balises <script>
  container.querySelectorAll("script").forEach((oldScript) => {
    const newScript = document.createElement("script");
    Array.from(oldScript.attributes).forEach((attr) =>
      newScript.setAttribute(attr.name, attr.value)
    );
    newScript.textContent = oldScript.textContent;
    oldScript.parentNode.replaceChild(newScript, oldScript);
  });

  switch (location) {
    case "head":
      document.head.appendChild(container);
      break;
    case "body_start":
      document.body.insertBefore(container, document.body.firstChild);
      break;
    case "body_end":
    default:
      document.body.appendChild(container);
  }
}
