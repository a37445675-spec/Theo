export default function TextBlock({ config }) {
  return (
    <div className="container">
      <p className="block-text">{config?.text || ""}</p>
    </div>
  );
}
