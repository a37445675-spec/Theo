"""
Corrige l'installation de Vitest en installant les versions compatibles Vite 5.

Usage : python fix_vitest_install.py
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


SETUP_JS = '''import "@testing-library/jest-dom";
import { vi } from "vitest";

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

global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() { return []; }
};

global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

window.scrollTo = vi.fn();

global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(""),
  })
);

beforeEach(() => {
  localStorage.clear();
});
'''


TEST_UTILS = '''import { render } from "@testing-library/react";
import React from "react";
import { BrowserRouter } from "react-router-dom";

export function renderWithRouter(ui, options = {}) {
  return render(<BrowserRouter>{ui}</BrowserRouter>, options);
}

export function mockPuck(children = null) {
  return {
    DropZone: ({ zone }) => <div data-testid={`dropzone-${zone || "content"}`}>{children}</div>,
    renderDropZone: (opts) => <div data-testid={`dropzone-${opts?.zone || "content"}`}>{children}</div>,
  };
}

export function renderWidget(widget, props = {}) {
  const defaultProps = { ...(widget.defaultProps || {}), ...props };
  const Component = widget.render;
  return renderWithRouter(<Component {...defaultProps} puck={mockPuck()} />);
}

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


WIDGETS_INVENTORY = '''import * as mediaWidgets from "../puck/widgets/mediaWidgets";
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


SMOKE_TEST = '''import { describe, it, expect } from "vitest";
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


CORE_TEST = '''import { describe, it, expect } from "vitest";
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
});


describe("GridContainer", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(GridContainer);
    expect(container).toBeTruthy();
  });

  it("contient une zone de drop", () => {
    const { container } = renderWidget(GridContainer);
    expect(container.querySelector("[data-testid='dropzone-content']")).toBeInTheDocument();
  });
});


describe("Container", () => {
  it("rend sans crash avec les props par défaut", () => {
    const { container } = renderWidget(Container);
    expect(container).toBeTruthy();
  });

  it("contient une zone de drop", () => {
    const { container } = renderWidget(Container);
    expect(container.querySelector("[data-testid='dropzone-content']")).toBeInTheDocument();
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
});
'''


SERIES_TEST = '''import { describe, it, expect } from "vitest";
import { renderWidget } from "./test_utils";
import {
  PricingPro, CountdownPro, TeamGrid, FeatureList,
} from "../puck/widgets/widgetsSeries2";
import {
  FaqPro, TimelinePro, TrustBadgesPro,
} from "../puck/widgets/widgetsSeries3";
import {
  ChatWidgetPro, BackToTopPro, ScrollProgressPro, StickyCtaPro,
} from "../puck/widgets/widgetsSeries4";
import {
  SearchBarAdvanced, ProductComparator, MultiStepFormPro, QuizPro,
  WishlistPro, RecentlyViewedPro,
} from "../puck/widgets/widgetsSeries5";


describe("Série 2 — Marketing", () => {
  it("PricingPro affiche le nom du plan", () => {
    const { container } = renderWidget(PricingPro, { planName: "Test Plan" });
    expect(container.textContent).toContain("Test Plan");
  });

  it("CountdownPro affiche le titre", () => {
    const { container } = renderWidget(CountdownPro, { title: "Test Countdown" });
    expect(container.textContent).toContain("Test Countdown");
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


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")


def install_compatible_versions():
    """Installe Vitest 2.x compatible Vite 5."""
    print("\n[1/3] Installation des dépendances compatibles Vite 5...")

    # Versions compatibles Vite 5
    packages = [
        "vitest@^2.1.0",
        "@vitest/coverage-v8@^2.1.0",
        "@testing-library/react@^16.0.0",
        "@testing-library/jest-dom@^6.4.0",
        "@testing-library/user-event@^14.5.0",
        "jsdom@^24.0.0",
    ]

    try:
        subprocess.run(
            ["npm", "install", "--save-dev", "--legacy-peer-deps", *packages],
            cwd=BASE_DIR,
            check=True,
            shell=True,
        )
        print("  [OK] Dépendances installées (Vitest 2.x + Vite 5)")
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        print("\n  Essayez manuellement :")
        print("    npm install --save-dev --legacy-peer-deps vitest@^2.1.0 @vitest/coverage-v8@^2.1.0 @testing-library/react@^16.0.0 @testing-library/jest-dom@^6.4.0 @testing-library/user-event@^14.5.0 jsdom@^24.0.0")
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

    print("  [OK] Scripts : test, test:run, test:ui, test:coverage")


def create_test_files():
    print("\n[3/3] Création des fichiers de test...")

    write_file(os.path.join(BASE_DIR, "vitest.config.js"), VITEST_CONFIG)
    write_file(os.path.join(TESTS_DIR, "setup.js"), SETUP_JS)
    write_file(os.path.join(TESTS_DIR, "test_utils.jsx"), TEST_UTILS)
    write_file(os.path.join(TESTS_DIR, "widgets_inventory.js"), WIDGETS_INVENTORY)
    write_file(os.path.join(TESTS_DIR, "widgets.smoke.test.jsx"), SMOKE_TEST)
    write_file(os.path.join(TESTS_DIR, "widgets.core.test.jsx"), CORE_TEST)
    write_file(os.path.join(TESTS_DIR, "widgets.series.test.jsx"), SERIES_TEST)


def main():
    print("=" * 60)
    print("  INSTALLATION VITEST (COMPATIBLE VITE 5)")
    print("=" * 60)

    if not os.path.exists(PACKAGE_JSON):
        print(f"  [ERREUR] package.json introuvable")
        return

    install_compatible_versions()
    update_package_json()
    create_test_files()

    print()
    print("=" * 60)
    print("  ✅ TESTS INSTALLÉS")
    print("=" * 60)
    print("\nCommandes :")
    print("  npm run test:run       → tous les tests")
    print("  npm run test           → mode watch")
    print("  npm run test:ui        → interface graphique")
    print("  npm run test:coverage  → couverture")


if __name__ == "__main__":
    main()