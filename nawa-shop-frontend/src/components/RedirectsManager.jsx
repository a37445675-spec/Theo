import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * Gère les redirections dynamiques définies dans l'admin.
 * Ex : /ancienne-url → /nouvelle-url (301 ou 302)
 */
export default function RedirectsManager({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [redirects, setRedirects] = useState(null);

  useEffect(() => {
    fetch("/api/v1/redirects/")
      .then((res) => (res.ok ? res.json() : { results: [] }))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setRedirects(list);
      })
      .catch(() => setRedirects([]));
  }, []);

  useEffect(() => {
    if (!redirects) return;
    const match = redirects.find(
      (r) => r.is_active && r.old_path === location.pathname
    );
    if (match) {
      navigate(match.new_path, { replace: match.redirect_type === "301" });
    }
  }, [location.pathname, redirects, navigate]);

  return children;
}
