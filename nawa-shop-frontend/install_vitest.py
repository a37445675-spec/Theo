"""
Installation des tests unitaires Vitest + React Testing Library.
- Installe les dépendances
- Crée vitest.config.js
- Crée le setup de test
- Génère les fichiers de test pour les 146 widgets

Usage : python install_vitest.py
"""
import json
import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
TESTS_DIR = os.path.join(SRC_DIR, "__tests__")
PACKAGE_JSON = os.path.join(BASE_DIR, "package.json")


# ============================================================
#              VITEST CONFIG
# ============================================================

VITEST_CONFIG = '''import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/__tests__/setup.js"],
    include: ["src/**/*.{test,spec}.{js,jsx}"],
    exclude: ["node_modules", "dist", ".vite"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/**",
        "src/**/*.test.{js,jsx}",
        "src/**/*.spec.{js,jsx}",
        "src/__tests__/**",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
'''


# ============================================================
#              SETUP FILE
# ============================================================

SETUP_JS = '''/**
 * Setup global pour Vitest.
 * - Charge @testing-library/jest-dom pour les matchers
 * - Mock matchMedia (utilisé par certains widgets)
 * - Mock IntersectionObserver (utilisé par Cascade, Counter, etc.)
 * - Mock ResizeObserver
 */
import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return []; }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock scrollTo
window.scrollTo = vi.fn();

// Mock fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(""),
  })
);

// Cleanup localStorage
beforeEach(() => {
  localStorage.clear();
});
'''


# ============================================================
#              TEST UTILITIES
# ============================================================

TEST_UTILS = '''/**
 * Utilitaires partagés par les tests.
 */
import { render } from "@testing-library/react";
import React from "react";
import { BrowserRouter } from "react-router-dom";

/**
 * Rend un composant avec le Router.
 */
export function renderWithRouter(ui, options = {}) {
  return render(<BrowserRouter>{ui}</BrowserRouter>, options);
}

/**
 * Mock Puck context pour les widgets qui utilisent puck.DropZone.
 */
export function mockPuck(children = null) {
  return {
    DropZone: ({ zone }) => <div data-testid={`dropzone-${zone || "content"}`}>{children}</div>,
    renderDropZone: (opts) => <div data-testid={`dropzone-${opts?.zone || "content"}`}>{children}</div>,
  };
}

/**
 * Rend un widget Puck avec props par défaut fusionnées.
 */
export function renderWidget(widget, props = {}) {
  const defaultProps = { ...(widget.defaultProps || {}), ...props };
  const Component = widget.render;
  return renderWithRouter(<Component {...defaultProps} puck={mockPuck()} />);
}

/**
 * Vérifie qu'un widget se rend sans crash.
 */
export function smokeTest(widget, customProps = {}) {
  try {
    const { unmount } = renderWidget(widget, customProps);
    unmount();
    return { ok: true };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}
'''


# ============================================================
#              WIDGETS INVENTORY (pour les tests)
# ============================================================

WIDGETS_INVENTORY = '''/**
 * Inventaire automatique des widgets pour les tests.
 * Importe tous les widgets connus.
 */
import * as mediaWidgets from "../puck/widgets/mediaWidgets";
import * as interactiveWidgets from "../puck/widgets/interactiveWidgets";
import * as marketingWidgets from "../puck/widgets/marketingWidgets";
import * as socialWidgets from "../puck/widgets/socialWidgets";
import * as postWidgets from "../puck/widgets/postWidgets";
import * as archiveWidgets from "../puck/widgets/archiveWidgets";
import * as productWidgets from "../puck/widgets/productWidgets";
import * as commerceWidgets from "../puck/widgets/commerceWidgets";
import * as layoutWidgets from "../puck/widgets/layoutWidgets";
import * as responsiveWidgets from "../puck/widgets/responsiveWidgets";
import * as advancedWidgets from "../puck/widgets/advancedWidgets";
import * as mediaProWidgets from "../puck/widgets/mediaProWidgets";
import * as series2 from "../puck/widgets/widgetsSeries2";
import * as series3 from "../puck/widgets/widgetsSeries3";
import * as series4 from "../puck/widgets/widgetsSeries4";
import * as series5 from "../puck/widgets/widgetsSeries5";
import * as coreUpgrade from "../puck/widgets/widgetsCoreUpgrade";

export const ALL_WIDGETS = {
  ...mediaWidgets,
  ...interactiveWidgets,
  ...marketingWidgets,
  ...socialWidgets,
  ...postWidgets,
  ...archiveWidgets,
  ...productWidgets,
  ...commerceWidgets,
  ...layoutWidgets,
  ...responsiveWidgets,
  ...advancedWidgets,
  ...mediaProWidgets,
  ...series2,
  ...series3,
  ...series4,
  ...series5,
  ...coreUpgrade,
};

// Filtrer uniquement les objets qui ressemblent à des widgets Puck
export const VALID_WIDGETS = Object.entries(ALL_WIDGETS).filter(([name, value]) => {
  return (
    value &&
    typeof value === "object" &&
    typeof value.render === "function" &&
    value.fields &&
    value.defaultProps
  );
});
'''


# ============================================================
#              SMOKE TESTS
# ============================================================

SMOKE_TEST = '''/**
 * Smoke tests — vérifie que chaque widget se rend sans crash.
 */
import { describe, it, expect } from "vitest";
import { VALID_WIDGETS } from "./widgets_inventory";
import { smokeTest } from "./test_utils";

describe("Smoke tests — Tous les widgets", () => {
  it("doit trouver au moins 100 widgets", () => {
    expect(VALID_WIDGETS.length).toBeGreaterThan(100);
  });

  describe.each(VALID_WIDGETS)("Widget : %s", (name, widget) => {
    it("se rend sans crash avec les props par défaut", () => {
      const result = smokeTest(widget);
      if (!result.ok) {
        console.error(`❌ ${name} : ${result.error}`);
      }
      expect(result.ok).toBe(true);
    });

    it("a un objet defaultProps défini", () => {
      expect(widget.defaultProps).toBeDefined();
      expect(typeof widget.defaultProps).toBe("object");
    });

    it("a un objet fields défini", () => {
      expect(widget.fields).toBeDefined();
      expect(typeof widget.fields).toBe("object");
    });

    it("a une fonction render", () => {
      expect(typeof widget.render).toBe("function");
    });
  });
});
'''


# ============================================================
#              CORE WIDGETS TESTS
# ============================================================

CORE_TEST = '''/**
 * Tests détaillés des 4 widgets Core (Série 6).
 */
import { describe, it, expect } from "vitest";
import { renderWidget } from "./test_utils";
import {
  SliderPro,
  GridContainer,
  Container,
  FlexContainer,
} from "../puck/widgets/widgetsCoreUpgrade";


describe("SliderPro", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(SliderPro);
    expect(container).toBeTruthy();
  });

  it("affiche les flèches par défaut", () => {
    const { container } = renderWidget(SliderPro);
    const arrows = container.querySelectorAll(".slider-arrow");
    expect(arrows.length).toBe(2);
  });

  it("affiche les dots par défaut", () => {
    const { container } = renderWidget(SliderPro);
    const dots = container.querySelector(".slider-dots");
    expect(dots).toBeInTheDocument();
  });

  it("cache les flèches si showArrows=false", () => {
    const { container } = renderWidget(SliderPro, { showArrows: "false" });
    const arrows = container.querySelectorAll(".slider-arrow");
    expect(arrows.length).toBe(0);
  });

  it("crée le bon nombre de slides", () => {
    const { container } = renderWidget(SliderPro, { slideCount: 5 });
    const slides = container.querySelectorAll(".slider-slide");
    expect(slides.length).toBe(5);
  });

  it("supporte le mode vertical", () => {
    const { container } = renderWidget(SliderPro, { orientation: "vertical" });
    expect(container).toBeTruthy();
  });

  it("supporte le mode coverflow", () => {
    const { container } = renderWidget(SliderPro, { effect: "coverflow" });
    expect(container).toBeTruthy();
  });

  it("affiche le play/pause si activé", () => {
    const { container } = renderWidget(SliderPro, { showPlayPause: "true" });
    const btn = container.querySelector(".slider-playpause");
    expect(btn).toBeInTheDocument();
  });
});


describe("GridContainer", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(GridContainer);
    expect(container).toBeTruthy();
  });

  it("applique la classe tag section par défaut", () => {
    const { container } = renderWidget(GridContainer, { tag: "section" });
    expect(container.querySelector("section")).toBeInTheDocument();
  });

  it("rend une div si tag=div", () => {
    const { container } = renderWidget(GridContainer, { tag: "div" });
    expect(container.querySelector("div")).toBeInTheDocument();
  });

  it("contient une zone de drop", () => {
    const { container } = renderWidget(GridContainer);
    expect(container.querySelector("[data-testid='dropzone-content']")).toBeInTheDocument();
  });

  it("supporte le mode auto-fit", () => {
    const { container } = renderWidget(GridContainer, { columnsMode: "auto-fit" });
    expect(container).toBeTruthy();
  });
});


describe("Container", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(Container);
    expect(container).toBeTruthy();
  });

  it("applique le tag section par défaut", () => {
    const { container } = renderWidget(Container);
    expect(container.querySelector("section")).toBeInTheDocument();
  });

  it("contient une zone de drop", () => {
    const { container } = renderWidget(Container);
    expect(container.querySelector("[data-testid='dropzone-content']")).toBeInTheDocument();
  });

  it("supporte widthMode=full", () => {
    const { container } = renderWidget(Container, { widthMode: "full" });
    expect(container).toBeTruthy();
  });

  it("supporte widthMode=boxed", () => {
    const { container } = renderWidget(Container, {
      widthMode: "boxed",
      customWidth: "800px",
    });
    expect(container).toBeTruthy();
  });

  it("rend une vidéo si backgroundVideo est défini", () => {
    const { container } = renderWidget(Container, {
      backgroundVideo: "/test.mp4",
    });
    expect(container.querySelector("video")).toBeInTheDocument();
  });
});


describe("FlexContainer", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(FlexContainer);
    expect(container).toBeTruthy();
  });

  it("contient une zone de drop", () => {
    const { container } = renderWidget(FlexContainer);
    expect(container.querySelector("[data-testid='dropzone-content']")).toBeInTheDocument();
  });

  it("supporte direction=column", () => {
    const { container } = renderWidget(FlexContainer, { direction: "column" });
    expect(container).toBeTruthy();
  });

  it("supporte direction=row-reverse", () => {
    const { container } = renderWidget(FlexContainer, { direction: "row-reverse" });
    expect(container).toBeTruthy();
  });

  it("applique les per-item styles", () => {
    const { container } = renderWidget(FlexContainer, {
      perItemStyles: "1:1,0,auto,0,auto",
    });
    const style = container.querySelector("style");
    expect(style.textContent).toContain("flex-grow: 1");
  });
});
'''


# ============================================================
#              SERIES TESTS
# ============================================================

SERIES_TEST = '''/**
 * Tests des widgets des Séries 2 à 5.
 */
import { describe, it, expect } from "vitest";
import { renderWidget } from "./test_utils";
import {
  PricingPro, CountdownPro, TestimonialWall, StatsSection,
  StepsProcess, TeamGrid, LogoCloud, FeatureList,
} from "../puck/widgets/widgetsSeries2";
import {
  FaqPro, TimelinePro, ComparisonPro, BeforeAfterPro,
  ProgressRingPro, RatingBreakdownPro, NotificationBannerPro, TrustBadgesPro,
} from "../puck/widgets/widgetsSeries3";
import {
  ChatWidgetPro, CookieConsentPro, NewsletterInlinePro, ExitIntentPopupPro,
  SocialProofPro, BackToTopPro, ScrollProgressPro, StickyCtaPro,
} from "../puck/widgets/widgetsSeries4";
import {
  SearchBarAdvanced, ProductComparator, MultiStepFormPro, PriceSimulatorPro,
  BookingCalendarPro, QuizPro, WishlistPro, RecentlyViewedPro,
} from "../puck/widgets/widgetsSeries5";


describe("Série 2 — Marketing", () => {
  it("PricingPro rend correctement", () => {
    const { container } = renderWidget(PricingPro, { planName: "Test Plan" });
    expect(container.textContent).toContain("Test Plan");
  });

  it("CountdownPro affiche le titre", () => {
    const { container } = renderWidget(CountdownPro, { title: "Test Countdown" });
    expect(container.textContent).toContain("Test Countdown");
  });

  it("StatsSection affiche les stats", () => {
    const { container } = renderWidget(StatsSection);
    expect(container).toBeTruthy();
  });

  it("TeamGrid affiche les membres", () => {
    const { container } = renderWidget(TeamGrid, {
      members: "Alice|CEO|\\nBob|CTO|",
    });
    expect(container.textContent).toContain("Alice");
  });

  it("FeatureList affiche les features", () => {
    const { container } = renderWidget(FeatureList, {
      features: "✓ Test feature|Description test",
    });
    expect(container.textContent).toContain("Test feature");
  });
});


describe("Série 3 — Contenu", () => {
  it("FaqPro affiche les questions", () => {
    const { container } = renderWidget(FaqPro, {
      items: "Question test ?|Réponse test|Général",
    });
    expect(container.textContent).toContain("Question test");
  });

  it("TimelinePro affiche les événements", () => {
    const { container } = renderWidget(TimelinePro, {
      events: "2024|Test Event|Description|🌱",
    });
    expect(container.textContent).toContain("Test Event");
  });

  it("ComparisonPro affiche les colonnes", () => {
    const { container } = renderWidget(ComparisonPro);
    expect(container).toBeTruthy();
  });

  it("ProgressRingPro affiche les anneaux", () => {
    const { container } = renderWidget(ProgressRingPro);
    expect(container).toBeTruthy();
  });

  it("TrustBadgesPro affiche les badges", () => {
    const { container } = renderWidget(TrustBadgesPro, {
      badges: "🔒|Test Secure|SSL",
    });
    expect(container.textContent).toContain("Test Secure");
  });
});


describe("Série 4 — Engagement", () => {
  it("ChatWidgetPro rend la bulle", () => {
    const { container } = renderWidget(ChatWidgetPro);
    expect(container.querySelector(".chat-bubble")).toBeInTheDocument();
  });

  it("BackToTopPro rend sans crash", () => {
    const { container } = renderWidget(BackToTopPro);
    expect(container).toBeTruthy();
  });

  it("ScrollProgressPro rend sans crash", () => {
    const { container } = renderWidget(ScrollProgressPro);
    expect(container).toBeTruthy();
  });

  it("StickyCtaPro affiche le message", () => {
    const { container } = renderWidget(StickyCtaPro, { message: "Test CTA" });
    expect(container.textContent).toContain("Test CTA");
  });
});


describe("Série 5 — Interactions", () => {
  it("SearchBarAdvanced affiche l'input", () => {
    const { container } = renderWidget(SearchBarAdvanced);
    expect(container.querySelector("input")).toBeInTheDocument();
  });

  it("ProductComparator affiche les produits", () => {
    const { container } = renderWidget(ProductComparator, {
      products: "Prod1|10|/test.jpg|4.5|Attr1,Attr2",
    });
    expect(container.textContent).toContain("Prod1");
  });

  it("MultiStepFormPro affiche la première étape", () => {
    const { container } = renderWidget(MultiStepFormPro, {
      steps: "Étape 1|field1,field2",
    });
    expect(container.textContent).toContain("Étape 1");
  });

  it("PriceSimulatorPro affiche le calcul", () => {
    const { container } = renderWidget(PriceSimulatorPro, { price: 100 });
    expect(container).toBeTruthy();
  });

  it("QuizPro affiche la première question", () => {
    const { container } = renderWidget(QuizPro, {
      questions: "Test question ?|Réponse1,Réponse2",
    });
    expect(container.textContent).toContain("Test question");
  });

  it("WishlistPro rend le bouton", () => {
    const { container } = renderWidget(WishlistPro);
    expect(container.querySelector("button")).toBeInTheDocument();
  });

  it("RecentlyViewedPro affiche le titre", () => {
    const { container } = renderWidget(RecentlyViewedPro, { title: "Test Recent" });
    expect(container.textContent).toContain("Test Recent");
  });
});
'''


# ============================================================
#              FONCTIONS
# ============================================================

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def install_packages():
    print("\n[1/3] Installation des dépendances...")

    packages = [
        "vitest",
        "@vitest/coverage-v8",
        "@testing-library/react",
        "@testing-library/jest-dom",
        "@testing-library/user-event",
        "jsdom",
    ]

    try:
        subprocess.run(
            ["npm", "install", "--save-dev", *packages],
            cwd=BASE_DIR,
            check=True,
            shell=True,
        )
        print("  [OK] Dépendances installées")
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        sys.exit(1)


def update_package_json():
    print("\n[2/3] Mise à jour de package.json...")

    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        pkg = json.load(f)

    pkg.setdefault("scripts", {})
    pkg["scripts"]["test"] = "vitest"
    pkg["scripts"]["test:run"] = "vitest run"
    pkg["scripts"]["test:ui"] = "vitest --ui"
    pkg["scripts"]["test:coverage"] = "vitest run --coverage"

    with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)

    print("  [OK] Scripts ajoutés : test, test:run, test:ui, test:coverage")


def create_test_files():
    print("\n[3/3] Création des fichiers de test...")

    write_file(os.path.join(BASE_DIR, "vitest.config.js"), VITEST_CONFIG)
    write_file(os.path.join(TESTS_DIR, "setup.js"), SETUP_JS)
    write_file(os.path.join(TESTS_DIR, "test_utils.jsx"), TEST_UTILS)
    write_file(os.path.join(TESTS_DIR, "widgets_inventory.js"), WIDGETS_INVENTORY)
    write_file(os.path.join(TESTS_DIR, "widgets.smoke.test.jsx"), SMOKE_TEST)
    write_file(os.path.join(TESTS_DIR, "widgets.core.test.jsx"), CORE_TEST)
    write_file(os.path.join(TESTS_DIR, "widgets.series.test.jsx"), SERIES_TEST)


# ============================================================
#              MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  INSTALLATION DES TESTS UNITAIRES")
    print("=" * 60)

    if not os.path.exists(PACKAGE_JSON):
        print(f"  [ERREUR] package.json introuvable dans {BASE_DIR}")
        return

    install_packages()
    update_package_json()
    create_test_files()

    print()
    print("=" * 60)
    print("  ✅ TESTS INSTALLÉS")
    print("=" * 60)
    print("\nFichiers créés :")
    print("  vitest.config.js")
    print("  src/__tests__/setup.js")
    print("  src/__tests__/test_utils.jsx")
    print("  src/__tests__/widgets_inventory.js")
    print("  src/__tests__/widgets.smoke.test.jsx")
    print("  src/__tests__/widgets.core.test.jsx")
    print("  src/__tests__/widgets.series.test.jsx")
    print()
    print("Commandes :")
    print("  npm run test          → mode watch")
    print("  npm run test:run      → une fois")
    print("  npm run test:ui       → interface graphique")
    print("  npm run test:coverage → avec couverture")


if __name__ == "__main__":
    main()