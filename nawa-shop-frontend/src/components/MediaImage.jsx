/**
 * Composant image prêt pour la médiathèque.
 * Supporte le lazy loading, les fallbacks et les ratios.
 *
 * Usage :
 *   <MediaImage src="/media/x.jpg" alt="..." ratio="1/1" />
 *   <MediaImage src={product.image_url} fallback="/fallbacks/product-fallback.jpg" />
 */
export default function MediaImage({
  src,
  fallback = "/fallbacks/product-fallback.jpg",
  alt = "",
  className = "",
  ratio,
  width,
  height,
  loading = "lazy",
  ...props
}) {
  const style = ratio ? { aspectRatio: ratio, ...(props.style || {}) } : props.style;

  return (
    <img
      src={src || fallback}
      alt={alt}
      className={`media-image ${className}`}
      width={width}
      height={height}
      loading={loading}
      decoding="async"
      onError={(e) => {
        if (fallback && e.currentTarget.src !== fallback) {
          e.currentTarget.src = fallback;
        }
      }}
      style={style}
      {...props}
    />
  );
}
