(() => {
  "use strict";

  const storageKey = "instant-color-theme";
  const root = document.documentElement;
  const systemPreference = window.matchMedia("(prefers-color-scheme: dark)");

  function storedTheme() {
    try {
      const value = window.localStorage.getItem(storageKey);
      return value === "light" || value === "dark" ? value : null;
    } catch {
      return null;
    }
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    const color = document.querySelector("#theme-color");
    if (color) color.content = theme === "dark" ? "#0e1322" : "#d9e0e9";
    const toggle = document.querySelector("#theme-toggle");
    if (toggle) {
      const next = theme === "dark" ? "light" : "dark";
      toggle.setAttribute("aria-label", `Switch to ${next} theme`);
      toggle.setAttribute("title", `Switch to ${next} theme`);
    }
  }

  function setStoredTheme(theme) {
    try {
      window.localStorage.setItem(storageKey, theme);
    } catch {
      // The selected theme still applies for this page view.
    }
  }

  applyTheme(storedTheme() || (systemPreference.matches ? "dark" : "light"));

  document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.querySelector("#theme-toggle");
    themeToggle?.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      setStoredTheme(next);
      applyTheme(next);
    });

    const menu = document.querySelector("#docs-nav");
    const menuToggle = document.querySelector("#docs-menu-toggle");
    menuToggle?.addEventListener("click", () => {
      const open = menu?.dataset.open !== "true";
      if (menu) menu.dataset.open = String(open);
      menuToggle.setAttribute("aria-expanded", String(open));
    });
    menu?.addEventListener("click", (event) => {
      if (!(event.target instanceof HTMLAnchorElement)) return;
      delete menu.dataset.open;
      menuToggle?.setAttribute("aria-expanded", "false");
    });

    document.querySelectorAll("pre.command").forEach((pre) => {
      if (pre.dataset.copy === "false") return;
      pre.dataset.copy = "true";
      let wrapper = pre.closest(".docs-code");
      if (!wrapper) {
        wrapper = document.createElement("div");
        wrapper.className = "docs-code";
        pre.before(wrapper);
        wrapper.append(pre);
      }
      if (wrapper.querySelector(".code-copy")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "code-copy";
      button.textContent = "Copy";
      button.setAttribute("aria-label", "Copy command");
      button.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(pre.textContent.trim());
          button.textContent = "Copied";
          window.setTimeout(() => {
            button.textContent = "Copy";
          }, 1600);
        } catch {
          button.textContent = "Select";
        }
      });
      wrapper.append(button);
    });

    const tocLinks = Array.from(document.querySelectorAll(".docs-sidebar a[href*='#']"));
    if (tocLinks.length && "IntersectionObserver" in window) {
      const linksById = new Map(
        tocLinks.map((link) => {
          const url = new URL(link.href, window.location.href);
          return [url.hash.slice(1), link];
        }),
      );
      const targets = Array.from(linksById.keys())
        .map((id) => document.getElementById(id))
        .filter(Boolean);
      const observer = new IntersectionObserver(
        (entries) => {
          const visible = entries.find((entry) => entry.isIntersecting);
          if (!visible) return;
          tocLinks.forEach((link) => link.removeAttribute("aria-current"));
          linksById.get(visible.target.id)?.setAttribute("aria-current", "true");
        },
        { rootMargin: "-18% 0px -70% 0px" },
      );
      targets.forEach((target) => observer.observe(target));
    }

    document.querySelectorAll("[data-current-year]").forEach((element) => {
      element.textContent = String(new Date().getFullYear());
    });
  });

  const followSystemTheme = (event) => {
    if (!storedTheme()) applyTheme(event.matches ? "dark" : "light");
  };
  if (typeof systemPreference.addEventListener === "function") {
    systemPreference.addEventListener("change", followSystemTheme);
  } else {
    systemPreference.addListener(followSystemTheme);
  }
})();
