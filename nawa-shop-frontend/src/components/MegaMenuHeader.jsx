import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/**
 * MegaMenu Header — auto-suffisant.
 * Fetch directement /api/v1/navigation/menus/?location=header
 * Affiche les items avec leurs enfants en dropdown au survol.
 */
export default function MegaMenuHeader() {
  const [menu, setMenu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openItem, setOpenItem] = useState(null);

  useEffect(() => {
    fetch("/api/v1/navigation/menus/?location=header")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setMenu(list[0] || null);
      })
      .catch((err) => {
        console.warn("Mega menu indisponible:", err);
        setMenu(null);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return null;
  if (!menu || !menu.items || menu.items.length === 0) return null;

  return (
    <nav className="mega-menu-header">
      <ul className="mega-menu-list">
        {menu.items.map((item) => {
          const hasChildren = item.children && item.children.length > 0;

          return (
            <li
              key={item.id}
              className="mega-menu-item"
              onMouseEnter={() => hasChildren && setOpenItem(item.id)}
              onMouseLeave={() => setOpenItem(null)}
            >
              {item.url ? (
                <Link to={item.url} className="mega-menu-link">
                  {item.label}
                  {hasChildren && <span className="mega-arrow"> ▾</span>}
                </Link>
              ) : (
                <span className="mega-menu-link" style={{ cursor: "pointer" }}>
                  {item.label}
                  {hasChildren && <span className="mega-arrow"> ▾</span>}
                </span>
              )}

              {hasChildren && openItem === item.id && (
                <div className="mega-dropdown">
                  <div className="mega-column-title">{item.label}</div>
                  <ul className="mega-sublist">
                    {item.children.map((child) => (
                      <li key={child.id}>
                        <Link to={child.url} className="mega-sublink">
                          {child.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
