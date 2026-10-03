import { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi";

/**
 * Bannière d'annonce affichée en haut du site.
 */
export default function AnnouncementBar({ position = "top_bar" }) {
  const { data: announcements } = useApi(
    `/api/v1/announcements/?position=${position}&is_active=true`
  );
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !announcements || announcements.length === 0) return null;

  const ann = Array.isArray(announcements) ? announcements[0] : announcements;

  return (
    <div
      className="announcement-bar"
      style={{ backgroundColor: ann.background_color, color: ann.text_color }}
    >
      <span>{ann.message}</span>
      {ann.link && (
        <a href={ann.link} className="announcement-link">
          {ann.link_label}
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
  );
}
