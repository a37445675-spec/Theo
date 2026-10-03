import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(null);

  // Charge le design system depuis l'API
  useEffect(() => {
    fetch("/api/v1/design-system/")
      .then((res) => res.json())
      .then((data) => {
        const config = Array.isArray(data) ? data[0] : data;
        setTheme(config);
        applyTheme(config);
      })
      .catch((err) => console.warn("Erreur chargement design system:", err));
  }, []);

  // Applique les variables CSS dynamiquement
  const applyTheme = (config) => {
    if (!config) return;
    const root = document.documentElement;
    const map = {
      "--color-primary": config.color_primary,
      "--color-secondary": config.color_secondary,
      "--color-bg": config.color_background,
      "--color-text": config.color_text,
      "--color-accent": config.color_accent,
      "--color-error": config.color_error,
      "--color-success": config.color_success,
      "--font-heading": config.font_heading,
      "--font-body": config.font_body,
      "--font-size-base": config.font_size_base,
      "--radius": config.border_radius,
      "--button-radius": config.button_radius,
      "--shadow-sm": config.shadow_sm,
      "--shadow-md": config.shadow_md,
      "--shadow-lg": config.shadow_lg,
    };
    Object.entries(map).forEach(([key, value]) => {
      if (value) root.style.setProperty(key, value);
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
