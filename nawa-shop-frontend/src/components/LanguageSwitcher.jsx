import { useTranslation } from "../context/TranslationContext";

/**
 * Sélecteur de langue : affiche les langues disponibles.
 * Usage : <LanguageSwitcher />
 */
export default function LanguageSwitcher({ className = "" }) {
  const { locale, setLocale, supportedLocales } = useTranslation();

  const LABELS = { fr: "FR", en: "EN" };

  return (
    <div className={`language-switcher ${className}`}>
      {supportedLocales.map((lang) => (
        <button
          key={lang}
          className={`lang-btn ${lang === locale ? "active" : ""}`}
          onClick={() => setLocale(lang)}
          aria-label={`Changer en ${lang}`}
        >
          {LABELS[lang] || lang.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
