import { useEffect, useState } from "react";
import { Render } from "@puckeditor/core";
import { useParams } from "react-router-dom";
import { puckConfig } from "../puck/config";
import SeoHead from "../components/SeoHead";

/**
 * Affiche une page construite avec Puck.
 * Route : /pages/:pageId
 *
 * Charge les widgets depuis /api/v1/cms/widgets/?page=:pageId
 * et les rend avec le composant <Render /> de Puck.
 */
export default function PuckPage() {
  const { pageId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/cms/pages/${pageId}/public/`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((response) => {
        // Nouvelle API : { page: {...}, widgets: [...] }
        const widgets = response.widgets || (Array.isArray(response) ? response : []);
        setData({
          content: widgets.map(widgetToPuck),
          root: { props: {} },
        });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [pageId]);

  if (loading) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#6B6259" }}>
        Chargement de la page...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#DC2626" }}>
        <h2>Erreur</h2>
        <p>{error}</p>
        <p style={{ fontSize: "0.85rem", opacity: 0.7 }}>
          Vérifiez que la page ID "{pageId}" existe dans l'admin.
        </p>
      </div>
    );
  }

  if (!data || data.content.length === 0) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#6B6259" }}>
        <h2>Page vide</h2>
        <p>Cette page ne contient aucun widget.</p>
        <p style={{ fontSize: "0.85rem", opacity: 0.7 }}>
          Ajoutez des widgets via l'éditeur : /admin/pages/{pageId}/builder
        </p>
      </div>
    );
  }

  return (
    <>
      <SeoHead
        title={`Page CMS #${pageId}`}
        description="Page éditée via l'éditeur Puck"
      />
      <Render config={puckConfig} data={data} />
    </>
  );
}

/**
 * Convertit un widget API en format Puck.
 */
function widgetToPuck(w) {
  return {
    type: w.widget_type || w.type,
    props: {
      id: `widget-${w.id}`,
      ...(w.content || {}),
      ...(w.style || {}),
      _children: (w.children || []).map(widgetToPuck),
    },
  };
}
