export function EmptyState({ icon = "🗂️", title, action }) {
  return (
    <div className="state-block">
      <span className="state-icon">{icon}</span>
      <h3>{title}</h3>
      {action}
    </div>
  );
}

export function ErrorState({ title = "Une erreur est survenue", text, onRetry }) {
  return (
    <div className="state-block state-error">
      <span className="state-icon">⚠️</span>
      <h3>{title}</h3>
      {text && <p className="muted">{text}</p>}
      {onRetry && (
        <button className="btn btn-ghost" onClick={onRetry}>
          Réessayer
        </button>
      )}
    </div>
  );
}
