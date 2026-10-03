import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const CmsContext = createContext(null);

export function CmsProvider({ children }) {
  const [cmsConfig, setCmsConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Récupère la config globale depuis l'API Django
    axios.get("/api/v1/design-system/active/")
      .then((res) => {
        // L'API peut renvoyer une liste ou un objet unique
        const data = Array.isArray(res.data) ? res.data[0] : res.data;
        setCmsConfig(data);
      })
      .catch((err) => {
        console.warn("Impossible de charger la config CMS :", err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <CmsContext.Provider value={{ cmsConfig, loading }}>
      {children}
    </CmsContext.Provider>
  );
}

export function useCmsConfig() {
  const context = useContext(CmsContext);
  if (!context) {
    throw new Error("useCmsConfig doit être utilisé dans un CmsProvider");
  }
  return context;
}
