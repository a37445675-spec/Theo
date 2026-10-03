export function SkeletonLine({ width = "100%" }) {
  return <div className="skeleton-block skeleton-line" style={{ width }} />;
}

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-block skeleton-media" />
      <SkeletonLine width="70%" />
      <SkeletonLine width="40%" />
    </div>
  );
}

export function SkeletonGrid({ count = 8 }) {
  return (
    <div className="product-grid">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
