import { Puck } from "@puckeditor/core";
import "@puckeditor/core/puck.css";
import { useEffect, useState } from "react";
import { puckConfig } from "../../puck/config";
import { api } from "../../utils/api";

/**
 * Éditeur visuel drag-and-drop.
 * Route : /admin/pages/:pageId/builder
 */
export default function PageBuilder({ pageId }) {
  const [data, setData] = useState({ content: [], root: { props: {} } });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/cms/widgets/?page=${pageId}`)
      .then((res) => {
        const widgets = Array.isArray(res) ? res : res.results || [];
        setData({
          content: widgets.map(widgetToPuck),
          root: { props: {} },
        });
      })
      .catch(() => setData({ content: [], root: { props: {} } }))
      .finally(() => setLoading(false));
  }, [pageId]);

  const handlePublish = async (newData) => {
    try {
      await api.post("/cms/widgets/save-tree/", {
        page: pageId,
        tree: newData.content.map(puckToWidget),
      });
      alert("✅ Page sauvegardée avec succès !");
    } catch (err) {
      alert("❌ Erreur de sauvegarde : " + err.message);
    }
  };

  if (loading) return <div style={{ padding: "2rem" }}>Chargement de l'éditeur...</div>;

  return (
    <Puck
      config={puckConfig}
      data={data}
      onPublish={handlePublish}
      onChange={setData}
    />
  );
}


// ============================================================
//  Conversions API <-> Puck
// ============================================================

function widgetToPuck(w) {
  return {
    type: w.widget_type || w.type,
    props: {
      id: `widget-${w.id}`,
      ...(w.content || {}),
      ...(w.style || {}),
      ...(w.children ? { _children: w.children.map(widgetToPuck) } : {}),
    },
  };
}

function puckToWidget(node) {
  const { id, _children, ...props } = node.props || {};
  return {
    widget_type: node.type,
    content: props,
    style: {},
    children: (_children || []).map(puckToWidget),
  };
}
