import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/**
 * MegaMenu multi-niveaux — supporte N niveaux de sous-menus.
 * Fetch directement /api/v1/navigation/menus/?location=header
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
      .catch((err) => console.warn("Mega menu indisponible:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !menu || !menu.items || menu.items.length === 0) return null;

  return (
    <nav className="mega-menu-header">
      <ul className="mega-menu-list">
        {menu.items.map((item) => (
          <MegaItem
            key={item.id}
            item={item}
            isOpen={openItem === item.id}
            onOpen={() => setOpenItem(item.id)}
            onClose={() => setOpenItem(null)}
            level={0}
          />
        ))}
      </ul>
    </nav>
  );
}

/**
 * Rendu récursif d'un item de menu (supporte N niveaux).
 */
function MegaItem({ item, isOpen, onOpen, onClose, level }) {
  const hasChildren = item.children && item.children.length > 0;
  const isTopLevel = level === 0;

  // Niveau 0 (racine) : dropdown au survol
  if (isTopLevel) {
    return (
      <li
        className="mega-menu-item"
        onMouseEnter={hasChildren ? onOpen : undefined}
        onMouseLeave={hasChildren ? onClose : undefined}
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

        {hasChildren && isOpen && (
          <div className="mega-dropdown">
            <div className="mega-column-title">{item.label}</div>
            <ul className="mega-sublist">
              {item.children.map((child) => (
                <MegaItem
                  key={child.id}
                  item={child}
                  isOpen={false}
                  onOpen={() => {}}
                  onClose={() => {}}
                  level={1}
                />
              ))}
            </ul>
          </div>
        )}
      </li>
    );
  }

  // Niveaux 1+ : item avec sous-menu en cascade (au survol)
  return (
    <li
      className="mega-subitem"
      onMouseEnter={hasChildren ? onOpen : undefined}
      onMouseLeave={hasChildren ? onClose : undefined}
    >
      <Link to={item.url} className="mega-sublink">
        <span>{item.label}</span>
        {hasChildren && <span className="mega-cascade-arrow">›</span>}
      </Link>

      {hasChildren && isOpen && (
        <ul className="mega-cascade">
          {item.children.map((subChild) => (
            <MegaItem
              key={subChild.id}
              item={subChild}
              isOpen={false}
              onOpen={() => {}}
              onClose={() => {}}
              level={level + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}
