// ============================================================
//  main.jsx — Point d'entrée de NAWA Commerce
// ============================================================

// === Configuration globale (AVANT tout) ===
import "./api/axiosConfig"; // Client axios configuré (CSRF + JWT)

// === React ===
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

// === App ===
import App from "./App.jsx";

// === Styles globaux ===
import "./index.css";


// ============================================================
//  RENDU
// ============================================================

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);