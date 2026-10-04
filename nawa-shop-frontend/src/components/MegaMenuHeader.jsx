import { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigation } from "../context/NavigationContext";

/**
 * MegaMenu avec colonnes pour le Header.
 * Lit le menu de location="header" et affiche les items parents
 * avec leurs enfants en colonnes déroulantes.
 */
export default function MegaMenuHeader() {
  const { getMenu, loading } = useNavigation();
  const [openItem, setOpenItem] = useState(null);
  const menu = getMenu("header");

  if (loading || !menu || !menu.items || menu.items.length === 0) return null;

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
                  {hasChildren && <span className="mega-arrow">▾</span>}
                </Link>
              ) : (
                <span className="mega-menu-link">
                  {item.label}
                  {hasChildren && <span className="mega-arrow">▾</span>}
                </span>
              )}

              {hasChildren && openItem === item.id && (
                <div className="mega-dropdown">
                  <div className="mega-dropdown-inner">
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
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
