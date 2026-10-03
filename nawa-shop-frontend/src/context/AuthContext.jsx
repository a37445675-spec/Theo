import { createContext, useContext, useEffect, useState } from "react";
import * as authApi from "../api/auth.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem("nawa_access");
    if (!access) {
      setLoading(false);
      return;
    }
    authApi
      .fetchMe()
      .then(setUser)
      .catch(() => authApi.logout())
      .finally(() => setLoading(false));
  }, []);

  async function login(username, password) {
    const me = await authApi.login(username, password);
    setUser(me);
    return me;
  }

  async function register(payload) {
    const me = await authApi.register(payload);
    setUser(me);
    return me;
  }

  function logout() {
    authApi.logout();
    setUser(null);
  }

  async function updateProfile(payload) {
    const me = await authApi.updateMe(payload);
    setUser(me);
    return me;
  }

  const roles = user?.roles || [];
  const isShopManager = roles.includes("shop_manager") || roles.includes("administrator");
  const isVendor = roles.includes("vendor");

  const value = {
    user, loading, isAuthenticated: !!user, isShopManager, isVendor,
    login, register, logout, updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
