import { createContext, useContext, useEffect, useState } from "react";

const TranslationContext = createContext({});

export function TranslationProvider({ children, locale = "fr" }) {
  const [translations, setTranslations] = useState({});

  useEffect(() => {
    fetch(`/api/v1/translations/?lang=${locale}`)
      .then((res) => res.json())
      .then((data) => {
        const map = {};
        (Array.isArray(data) ? data : data.results || []).forEach((t) => {
          map[t.key] = t[`value_${locale}`] || t.value_fr || t.key;
        });
        setTranslations(map);
      })
      .catch((err) => console.warn("Erreur chargement traductions:", err));
  }, [locale]);

  return (
    <TranslationContext.Provider value={translations}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const translations = useContext(TranslationContext);
  return {
    t: (key, fallback) => translations[key] || fallback || key,
    locale: "fr",
  };
}
