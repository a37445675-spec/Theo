import { Render } from "@puckeditor/core";
import { useEffect, useState } from "react";
import { puckConfig } from "../puck/config";

/**
 * Rendu public d'une page sauvegardée.
 * Usage : <PublicPageRenderer pageId={1} />
 */
export default function PublicPageRenderer({ pageId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/cms/widgets/?page=${pageId}`)
      .then((res) => res.json())
      .then((widgets) => {
        const list = Array.isArray(widgets) ? widgets : widgets.results || [];
        setData({
          content: list.map(widgetToPuck),
          root: { props: {} },
        });
      });
  }, [pageId]);

  if (!data) return <div className="page-loading">Chargement...</div>;

  return <Render config={puckConfig} data={data} />;
}

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
