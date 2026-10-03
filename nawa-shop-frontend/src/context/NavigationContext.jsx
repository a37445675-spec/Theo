import { createContext, useContext, useEffect, useState } from "react";

const NavigationContext = createContext(null);

export function NavigationProvider({ children }) {
  const [menus, setMenus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/navigation/menus/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        // L'API peut renvoyer une liste ou un objet paginé
        const list = Array.isArray(data) ? data : (data.results || []);
        // Index par emplacement (header, footer, mobile)
        const byLocation = {};
        list.forEach((menu) => {
          if (!byLocation[menu.location]) {
            byLocation[menu.location] = menu;
          }
        });
        setMenus(byLocation);
      })
      .catch((err) => console.warn("Erreur chargement navigation:", err))
      .finally(() => setLoading(false));
  }, []);

  const getMenu = (location) => menus[location] || null;

  return (
    <NavigationContext.Provider value={{ menus, getMenu, loading }}>
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  const ctx = useContext(NavigationContext);
  if (!ctx) throw new Error("useNavigation doit être utilisé dans un NavigationProvider");
  return ctx;
}
