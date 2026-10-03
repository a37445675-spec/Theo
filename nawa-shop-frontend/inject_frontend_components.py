"""
Injection des composants frontend (Week 4, 5, 6).
Crée : FeatureFlagsContext, AnnouncementBar, ThirdPartyScripts,
       RedirectsManager, MediaImage.

Usage : python inject_frontend_components.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# ============================================================
#                  CONTENU DES FICHIERS
# ============================================================

FEATURE_FLAGS_CONTEXT = '''import { createContext, useContext, useEffect, useState, useCallback } from "react";

const FeatureFlagsContext = createContext(null);

export function FeatureFlagsProvider({ children }) {
  const [flags, setFlags] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/feature-flags/")
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        const map = {};
        list.forEach((flag) => {
          map[flag.code] = flag.is_enabled === true;
        });
        setFlags(map);
      })
      .catch((err) => console.warn("Feature flags indisponibles:", err))
      .finally(() => setLoading(false));
  }, []);

  const hasFlag = useCallback(
    (code) => {
      if (loading) return false;
      return flags[code] === true;
    },
    [flags, loading]
  );

  return (
    <FeatureFlagsContext.Provider value={{ flags, hasFlag, loading }}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

export function useFeatureFlags() {
  const ctx = useContext(FeatureFlagsContext);
  if (!ctx) throw new Error("useFeatureFlags doit être dans un FeatureFlagsProvider");
  return ctx;
}

export function useFeatureFlag(code) {
  const { hasFlag } = useFeatureFlags();
  return hasFlag(code);
}
'''


ANNOUNCEMENT_BAR = '''import { useState } from "react";
import { useApi } from "../hooks/useApi";

/**
 * Bannière d'annonce pilotée par le CMS.
 * position : "top_bar" | "popup" | "bottom"
 */
export default function AnnouncementBar({ position = "top_bar" }) {
  const { data: announcements } = useApi(
    `/api/v1/announcements/?position=${position}&is_active=true`
  );
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  const list = Array.isArray(announcements)
    ? announcements
    : announcements?.results || [];
  if (list.length === 0) return null;

  const ann = list[0];

  if (position === "popup") {
    return (
      <div className="announcement-popup-overlay" onClick={() => setDismissed(true)}>
        <div
          className="announcement-popup"
          onClick={(e) => e.stopPropagation()}
          style={{
            backgroundColor: ann.background_color,
            color: ann.text_color,
          }}
        >
          <p>{ann.message}</p>
          {ann.link && (
            <a href={ann.link} className="announcement-link">
              {ann.link_label || "En savoir plus"}
            </a>
          )}
          <button
            className="announcement-close"
            onClick={() => setDismissed(true)}
            aria-label="Fermer"
          >
            ×
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`announcement-bar announcement-${position}`}
      style={{
        backgroundColor: ann.background_color,
        color: ann.text_color,
      }}
    >
      <span className="announcement-message">{ann.message}</span>
      {ann.link && (
        <a href={ann.link} className="announcement-link">
          {ann.link_label || "En savoir plus"}
        </a>
      )}
      <button
        className="announcement-close"
        onClick={() => setDismissed(true)}
        aria-label="Fermer l'annonce"
      >
        ×
      </button>
    </div>
  );
}
'''


THIRD_PARTY_SCRIPTS = '''import { useEffect } from "react";

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
'''


REDIRECTS_MANAGER = '''import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * Gère les redirections dynamiques définies dans l'admin.
 * Ex : /ancienne-url → /nouvelle-url (301 ou 302)
 */
export default function RedirectsManager({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [redirects, setRedirects] = useState(null);

  useEffect(() => {
    fetch("/api/v1/redirects/")
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setRedirects(list);
      })
      .catch(() => setRedirects([]));
  }, []);

  useEffect(() => {
    if (!redirects) return;
    const match = redirects.find(
      (r) => r.is_active && r.old_path === location.pathname
    );
    if (match) {
      navigate(match.new_path, { replace: match.redirect_type === "301" });
    }
  }, [location.pathname, redirects, navigate]);

  return children;
}
'''


MEDIA_IMAGE = '''/**
 * Composant image prêt pour la médiathèque.
 * Supporte le lazy loading, les fallbacks et les ratios.
 *
 * Usage :
 *   <MediaImage src="/media/x.jpg" alt="..." ratio="1/1" />
 *   <MediaImage src={product.image_url} fallback="/fallbacks/product-fallback.jpg" />
 */
export default function MediaImage({
  src,
  fallback = "/fallbacks/product-fallback.jpg",
  alt = "",
  className = "",
  ratio,
  width,
  height,
  loading = "lazy",
  ...props
}) {
  const style = ratio ? { aspectRatio: ratio, ...(props.style || {}) } : props.style;

  return (
    <img
      src={src || fallback}
      alt={alt}
      className={`media-image ${className}`}
      width={width}
      height={height}
      loading={loading}
      decoding="async"
      onError={(e) => {
        if (fallback && e.currentTarget.src !== fallback) {
          e.currentTarget.src = fallback;
        }
      }}
      style={style}
      {...props}
    />
  );
}
'''


# ============================================================
#                    FONCTIONS UTILITAIRES
# ============================================================

FILES = {
    "context/FeatureFlagsContext.jsx": FEATURE_FLAGS_CONTEXT,
    "components/AnnouncementBar.jsx": ANNOUNCEMENT_BAR,
    "components/ThirdPartyScripts.jsx": THIRD_PARTY_SCRIPTS,
    "components/RedirectsManager.jsx": REDIRECTS_MANAGER,
    "components/MediaImage.jsx": MEDIA_IMAGE,
}


def write_file(relative_path, content):
    full_path = os.path.join(SRC_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    label = os.path.relpath(full_path, BASE_DIR)

    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label} (déjà à jour)")
                return False
        shutil.copy2(full_path, full_path + ".bak")
        print(f"  [BACKUP] {label}.bak")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def main():
    print("=" * 60)
    print("  INJECTION COMPOSANTS FRONTEND (Week 4, 5, 6)")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] Dossier src/ introuvable dans {BASE_DIR}")
        print("  Êtes-vous bien à la racine du frontend (nawa-shop-frontend) ?")
        return

    print()
    created = 0
    for path, content in FILES.items():
        if write_file(path, content):
            created += 1

    print()
    print("=" * 60)
    print(f"  TERMINÉ — {created} fichier(s) créé(s)/mis à jour.")
    print("=" * 60)


if __name__ == "__main__":
    main()