import { Link } from "react-router-dom";

export default function ButtonBlock({ config }) {
  if (!config?.label) return null;
  return (
    <div className="container" style={{ textAlign: "center" }}>
      <Link to={config.href || "/"} className="btn btn-primary btn-lg">{config.label}</Link>
    </div>
  );
}
