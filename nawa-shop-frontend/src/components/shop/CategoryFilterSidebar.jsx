import { attributeLabel } from "../../utils.js";

/**
 * Génère dynamiquement les filtres selon l'AttributeSet de la catégorie
 * (retourné par GET /api/catalog/categories/{slug}/attributes/) — un
 * vêtement affiche taille/couleur, un électroménager affiche voltage/garantie,
 * sans aucune logique de filtre codée en dur par verticale.
 */
export default function CategoryFilterSidebar({ attributeSet, activeFilters, onChange, onClear }) {
  if (!attributeSet) return null;

  function setFilter(code, value) {
    onChange({ ...activeFilters, [code]: value });
  }

  function toggleMultiValue(code, value) {
    const current = activeFilters[code] ? activeFilters[code].split(",") : [];
    const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value];
    setFilter(code, next.join(","));
  }

  const hasActiveFilters = Object.values(activeFilters).some(Boolean);

  return (
    <aside className="shop-filters">
      <div className="section-header-row">
        <h3>Filtres</h3>
        {hasActiveFilters && (
          <button className="link-arrow" onClick={onClear}>Réinitialiser</button>
        )}
      </div>
      {attributeSet.items.map(({ attribute }) => (
        <div className="filter-group" key={attribute.code}>
          <h4>{attributeLabel(attribute.code)}{attribute.unit ? ` (${attribute.unit})` : ""}</h4>

          {(attribute.attributeType === "single_choice") && (
            <div className="filter-list">
              {attribute.choices.map((choice) => (
                <button
                  key={choice}
                  className={activeFilters[attribute.code] === choice ? "active" : ""}
                  onClick={() => setFilter(attribute.code, activeFilters[attribute.code] === choice ? "" : choice)}
                >
                  {choice}
                </button>
              ))}
            </div>
          )}

          {attribute.attributeType === "multi_choice" && (
            <div className="filter-list">
              {attribute.choices.map((choice) => {
                const selected = (activeFilters[attribute.code] || "").split(",").includes(choice);
                return (
                  <button key={choice} className={selected ? "active" : ""} onClick={() => toggleMultiValue(attribute.code, choice)}>
                    {choice}
                  </button>
                );
              })}
            </div>
          )}

          {attribute.attributeType === "number" && (
            <div className="filter-range">
              <input
                type="number" placeholder="min"
                value={activeFilters[`${attribute.code}_min`] || ""}
                onChange={(e) => setFilter(`${attribute.code}_min`, e.target.value)}
              />
              <span>–</span>
              <input
                type="number" placeholder="max"
                value={activeFilters[`${attribute.code}_max`] || ""}
                onChange={(e) => setFilter(`${attribute.code}_max`, e.target.value)}
              />
            </div>
          )}

          {attribute.attributeType === "boolean" && (
            <label className="filter-checkbox">
              <input
                type="checkbox"
                checked={activeFilters[attribute.code] === "true"}
                onChange={(e) => setFilter(attribute.code, e.target.checked ? "true" : "")}
              />
              Oui uniquement
            </label>
          )}
        </div>
      ))}
    </aside>
  );
}
