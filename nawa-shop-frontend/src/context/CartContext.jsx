import { createContext, useCallback, useContext, useEffect, useState } from "react";
import * as cartApi from "../api/cart.js";
import { useAuth } from "./AuthContext.jsx";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const data = await cartApi.getCart();
      setCart(data);
    } catch {
      setCart(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh, isAuthenticated]);

  function showToast(message) {
    setToast(message);
    setTimeout(() => setToast(null), 2200);
  }

  async function addItem(product, variant, quantity = 1) {
    const data = await cartApi.addLine({ productId: product.id, variantId: variant?.id ?? null, quantity });
    setCart(data);
    showToast(`${product.name} ajouté au panier`);
    return data;
  }

  async function updateQuantity(lineId, quantity) {
    const data = await cartApi.updateLine(lineId, quantity);
    setCart(data);
    return data;
  }

  async function removeLine(lineId) {
    const data = await cartApi.removeLine(lineId);
    setCart(data);
    showToast("Article retiré du panier");
    return data;
  }

  const value = {
    cart, loading, toast, refresh, addItem, updateQuantity, removeLine,
    itemCount: cart?.totalItems ?? 0,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  return useContext(CartContext);
}
