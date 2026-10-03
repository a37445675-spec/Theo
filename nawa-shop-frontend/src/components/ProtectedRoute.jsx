import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function ProtectedRoute({ children, requireShopManager = false }) {
  const { isAuthenticated, isShopManager, loading } = useAuth();
  const location = useLocation();

  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/connexion" state={{ from: location }} replace />;
  if (requireShopManager && !isShopManager) return <Navigate to="/compte" replace />;
  return children;
}
