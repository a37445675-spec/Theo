import { createContext, useContext, useEffect, useState } from "react";

const SiteConfigContext = createContext(null);

export function SiteConfigProvider({ children }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Appel unique pour récupérer toute la config du site
    fetch("/api/v1/site-config/")
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch((err) => console.warn("Erreur chargement config site:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <SiteConfigContext.Provider value={{ config, loading }}>
      {children}
    </SiteConfigContext.Provider>
  );
}

export function useSiteConfig() {
  return useContext(SiteConfigContext);
}
