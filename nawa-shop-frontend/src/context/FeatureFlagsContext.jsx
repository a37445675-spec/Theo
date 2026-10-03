import { createContext, useContext, useEffect, useState } from "react";

const FeatureFlagsContext = createContext({});

export function FeatureFlagsProvider({ children }) {
  const [flags, setFlags] = useState({});

  useEffect(() => {
    fetch("/api/v1/feature-flags/")
      .then((res) => res.json())
      .then((data) => {
        const map = {};
        (Array.isArray(data) ? data : data.results || []).forEach((flag) => {
          map[flag.code] = flag.is_enabled;
        });
        setFlags(map);
      })
      .catch((err) => console.warn("Erreur chargement feature flags:", err));
  }, []);

  return (
    <FeatureFlagsContext.Provider value={flags}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

export function useFeatureFlags() {
  return useContext(FeatureFlagsContext);
}

export function useFeatureFlag(code) {
  const flags = useContext(FeatureFlagsContext);
  return flags[code] === true;
}
