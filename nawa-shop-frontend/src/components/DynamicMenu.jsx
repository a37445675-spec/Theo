import { Link } from "react-router-dom";
import { useApi } from "../hooks/useApi";

/**
 * Menu dynamique piloté par l'API.
 * Usage : <DynamicMenu location="header" />
 */
export default function DynamicMenu({ location = "header" }) {
  const { data: menus, loading } = useApi(`/api/v1/navigation/menus/?location=${location}`);

  if (loading || !menus) return null;

  const menu = Array.isArray(menus) ? menus[0] : menus;

  const renderItem = (item) => (
    <li key={item.id} className="menu-item">
      <Link to={item.url} target={item.open_in_new_tab ? "_blank" : undefined}>
        {item.icon && <img src={item.icon} alt="" className="menu-icon" />}
        {item.label}
      </Link>
      {item.children?.length > 0 && (
        <ul className="submenu">
          {item.children.map(renderItem)}
        </ul>
      )}
    </li>
  );

  return (
    <nav className={`dynamic-menu dynamic-menu-${location}`}>
      <ul>{menu?.items?.map(renderItem)}</ul>
    </nav>
  );
}
