import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

/**
 * Liste des pages éditables (templates CMS).
 * Route : /admin/pages
 */
export default function AdminPagesList() {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/v1/cms/templates/", { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setPages(list);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "#6B6259" }}>
        Chargement des pages...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "#DC2626" }}>
        Erreur : {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Éditeur de pages</h1>
      <p style={{ color: "#6B6259", marginBottom: "2rem" }}>
        Sélectionnez une page pour l'éditer dans le constructeur visuel.
      </p>

      {pages.length === 0 ? (
        <div style={{
          padding: "3rem",
          textAlign: "center",
          background: "#F7F0E4",
          borderRadius: "12px",
          color: "#6B6259",
        }}>
          <p>Aucune page disponible.</p>
          <p style={{ fontSize: "0.9rem" }}>
            Créez-en une dans{" "}
            <a
              href="http://localhost:8000/admin/cms/pagetemplate/"
              target="_blank"
              rel="noreferrer"
              style={{ color: "#C1652F", textDecoration: "underline" }}
            >
              l'admin Django
            </a>.
          </p>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {pages.map((page) => (
            <li
              key={page.id}
              style={{
                padding: "1.25rem",
                borderBottom: "1px solid #eee",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "1rem",
              }}
            >
              <div>
                <strong style={{ fontSize: "1.05rem" }}>{page.name}</strong>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "4px" }}>
                  Type : {page.template_type || "—"} · ID : {page.id}
                </div>
              </div>
              <Link
                to={`/admin/pages/${page.id}/builder`}
                style={{
                  background: "#C1652F",
                  color: "#fff",
                  padding: "10px 20px",
                  borderRadius: "8px",
                  textDecoration: "none",
                  fontWeight: 600,
                  fontSize: "0.9rem",
                  whiteSpace: "nowrap",
                }}
              >
                Éditer
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
