// ============================================================
//  App.jsx — Point d'entrée de NAWA Commerce
//  Architecture : Headless CMS + 12 modules
// ============================================================

// === Bootstrap CSRF (doit être importé en premier) ===
import { bootstrapCsrf } from "./api/axiosConfig";
import PuckPage from "./pages/PuckPage.jsx";

// === Providers externes ===
import { HelmetProvider } from "react-helmet-async";
import { useEffect, lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

// === Providers internes ===
import { ThemeProvider } from "./context/ThemeContext";
import { CmsProvider, useCmsConfig } from "./context/CmsContext";
import { TranslationProvider } from "./context/TranslationContext";
import { FeatureFlagsProvider } from "./context/FeatureFlagsContext";
import { AuthProvider } from "./context/AuthContext.jsx";
import { CartProvider } from "./context/CartContext.jsx";
import { NavigationProvider } from "./context/NavigationContext";

// === Composants layout ===
import Header from "./components/Header.jsx";
import Footer from "./components/Footer.jsx";
import Toast from "./components/Toast.jsx";
import ScrollToTop from "./components/ScrollToTop.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import PageTransition from "./components/PageTransition.jsx";

// === Composants dynamiques ===
import AnnouncementBar from "./components/AnnouncementBar.jsx";
import ThirdPartyScripts from "./components/ThirdPartyScripts.jsx";
import RedirectsManager from "./components/RedirectsManager.jsx";

// === Pages ===
import Home from "./pages/Home.jsx";
import Shop from "./pages/Shop.jsx";
import ProductDetail from "./pages/ProductDetail.jsx";
import Cart from "./pages/Cart.jsx";
import Checkout from "./pages/Checkout.jsx";
import OrderConfirmation from "./pages/OrderConfirmation.jsx";
import BookingSlots from "./pages/BookingSlots.jsx";
import Blog from "./pages/Blog.jsx";
import BlogPost from "./pages/BlogPost.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Account from "./pages/Account.jsx";
import AccountOrders from "./pages/AccountOrders.jsx";
import AccountOrderDetail from "./pages/AccountOrderDetail.jsx";
import AccountAddresses from "./pages/AccountAddresses.jsx";
import AccountLoyalty from "./pages/AccountLoyalty.jsx";
import AccountSubscriptions from "./pages/AccountSubscriptions.jsx";
import AccountInvoices from "./pages/AccountInvoices.jsx";
import ManageOrders from "./pages/ManageOrders.jsx";
import NotFound from "./pages/NotFound.jsx";

// === Pages admin (Page Builder) ===
const AdminPagesList = lazy(() => import("./pages/admin/AdminPagesList.jsx"));
const PageBuilder = lazy(() => import("./pages/admin/PageBuilder.jsx"));

// ============================================================
//  Composants utilitaires (dans le scope des providers)
// ============================================================

/**
 * Met à jour dynamiquement le favicon depuis la config CMS.
 * Doit être DANS le CmsProvider.
 */
function FaviconManager() {
  const { cmsConfig } = useCmsConfig();

  useEffect(() => {
    if (!cmsConfig?.favicon) return;

    let link = document.querySelector("link[rel*='icon']");
    if (!link) {
      link = document.createElement("link");
      link.rel = "shortcut icon";
      document.head.appendChild(link);
    }
    link.type = "image/x-icon";
    link.href = cmsConfig.favicon;
  }, [cmsConfig]);

  return null;
}

// ============================================================
//  Composant principal
// ============================================================

export default function App() {
  // Bootstrap CSRF au démarrage (pour le panier anonyme)
  useEffect(() => {
    bootstrapCsrf();
  }, []);

  return (
    <HelmetProvider>
      <ThemeProvider>
        <CmsProvider>
          <TranslationProvider>
            <FeatureFlagsProvider>
              <AuthProvider>
                <CartProvider>
                  <NavigationProvider>
                    <RedirectsManager>
                      {/* === Injections globales === */}
                      <FaviconManager />
                      <ThirdPartyScripts />

                      {/* === Barre d'annonce (haut) === */}
                      <AnnouncementBar position="top_bar" />

                      {/* === Layout principal === */}
                      <ScrollToTop />
                      <Header />

                      <main className="site-main">
                        <PageTransition>
                          <Routes>
                            {/* ---- Boutique ---- */}
                            <Route path="/" element={<Home />} />
                            <Route path="/boutique/:categorySlug" element={<Shop />} />
                            <Route path="/produit/:slug" element={<ProductDetail />} />
                            <Route path="/reservations/:slug" element={<BookingSlots />} />

                            {/* ---- Panier & Commande ---- */}
                            <Route path="/panier" element={<Cart />} />
                            <Route path="/commande" element={<Checkout />} />
                            <Route
                              path="/commande/confirmation/:id"
                              element={<OrderConfirmation />}
                            />

                            {/* ---- Blog ---- */}
                            <Route path="/journal" element={<Blog />} />
                            <Route path="/journal/:slug" element={<BlogPost />} />

                            {/* ---- Authentification ---- */}
                            <Route path="/connexion" element={<Login />} />
                            <Route path="/inscription" element={<Register />} />

                            {/* ---- Compte client (protégé) ---- */}
                            <Route
                              path="/compte"
                              element={<ProtectedRoute><Account /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/commandes"
                              element={<ProtectedRoute><AccountOrders /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/commandes/:id"
                              element={<ProtectedRoute><AccountOrderDetail /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/adresses"
                              element={<ProtectedRoute><AccountAddresses /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/fidelite"
                              element={<ProtectedRoute><AccountLoyalty /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/abonnements"
                              element={<ProtectedRoute><AccountSubscriptions /></ProtectedRoute>}
                            />
                            <Route
                              path="/compte/factures"
                              element={<ProtectedRoute><AccountInvoices /></ProtectedRoute>}
                            />

                            {/* ---- Espace gestion (staff uniquement) ---- */}
                            <Route
                              path="/gestion/commandes"
                              element={
                                <ProtectedRoute requireShopManager>
                                  <ManageOrders />
                                </ProtectedRoute>
                              }
                            />

                            {/* ---- Admin : Page Builder (Widget Builder) ---- */}
                            <Route path="/admin/pages" element={<Suspense fallback={<div style={{padding: "3rem", textAlign: "center"}}>Chargement...</div>}><AdminPagesList /></Suspense>} />
                            <Route
                              path="/admin/pages/:pageId/builder"
                              element={<PageBuilder />}
                            />

                            {/* ---- 404 ---- */}
                                                        <Route path="/pages/:pageId" element={<PuckPage />} />

                            <Route path="*" element={<NotFound />} />
                          </Routes>
                        </PageTransition>
                      </main>

                      <Footer />

                      {/* === Popup d'annonce (au-dessus) === */}
                      <AnnouncementBar position="popup" />

                      <Toast />
                    </RedirectsManager>
                  </NavigationProvider>
                </CartProvider>
              </AuthProvider>
            </FeatureFlagsProvider>
          </TranslationProvider>
        </CmsProvider>
      </ThemeProvider>
    </HelmetProvider>
  );
}