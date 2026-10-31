/* Browser-local presentation only: no model execution or telemetry. */
(() => {
  "use strict";
  const ready = (fn) => document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", fn) : fn();
  ready(() => {
    const menu = document.querySelector(".oh-mobile-toggle");
    const nav = document.getElementById("oh-mobile-nav");
    if (menu && nav) {
      const close = () => { nav.hidden = true; menu.setAttribute("aria-expanded", "false"); menu.setAttribute("aria-label", "Open navigation"); };
      menu.addEventListener("click", () => {
        const open = menu.getAttribute("aria-expanded") !== "true";
        nav.hidden = !open;
        menu.setAttribute("aria-expanded", String(open));
        menu.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      });
      document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !nav.hidden) { close(); menu.focus(); } });
      window.addEventListener("resize", () => { if (window.innerWidth > 760) close(); });
    }

    const toast = document.createElement("div");
    toast.className = "oh-toast";
    toast.setAttribute("role", "status");
    toast.setAttribute("aria-live", "polite");
    toast.hidden = true;
    document.body.append(toast);
    let toastTimer;
    const notify = (text) => {
      clearTimeout(toastTimer); toast.textContent = text; toast.hidden = false;
      toastTimer = setTimeout(() => { toast.hidden = true; }, 2300);
    };
    document.querySelectorAll("[data-copy-code], [data-copy-target]").forEach((button) => {
      button.addEventListener("click", async () => {
        const target = button.dataset.copyTarget ? document.getElementById(button.dataset.copyTarget) : button.closest(".oh-code-window, .oh-model-example")?.querySelector("pre");
        if (!target) return;
        const value = target.textContent.trimEnd();
        try {
          if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(value);
          else {
            const field = document.createElement("textarea"); field.value = value;
            field.style.position = "fixed"; field.style.opacity = "0"; document.body.append(field); field.select();
            const copied = document.execCommand("copy"); field.remove();
            if (!copied) throw new Error("Clipboard is unavailable");
          }
          notify("Copied to clipboard");
        } catch (_) { notify("Select the code to copy it manually"); }
      });
    });

    const tabs = Array.from(document.querySelectorAll("[data-stage]"));
    function chooseStage(tab, focus = false) {
      tabs.forEach((item) => {
        const active = item === tab;
        item.setAttribute("aria-selected", String(active)); item.tabIndex = active ? 0 : -1;
        const panel = document.getElementById(item.getAttribute("aria-controls"));
        if (panel) panel.hidden = !active;
      });
      if (focus) { tab.focus(); tab.scrollIntoView({block: "nearest", inline: "nearest", behavior: "auto"}); }
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener("click", () => chooseStage(tab));
      tab.addEventListener("keydown", (event) => {
        let next;
        if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
        if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === "Home") next = 0;
        if (event.key === "End") next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); chooseStage(tabs[next], true); }
      });
    });

    const query = document.getElementById("oh-model-query");
    const access = document.getElementById("oh-access-filter");
    const buttons = Array.from(document.querySelectorAll("[data-category][aria-pressed]"));
    const rows = Array.from(document.querySelectorAll(".oh-model-row"));
    if (!query || !access || !rows.length) return;
    const initial = new URLSearchParams(window.location.search);
    let category = buttons.some((b) => b.dataset.category === initial.get("category")) ? initial.get("category") : "all";
    query.value = initial.get("q") || "";
    if (Array.from(access.options).some((item) => item.value === initial.get("access"))) access.value = initial.get("access");
    const reset = document.getElementById("oh-reset-filters");
    const noResults = document.getElementById("oh-no-results");
    const count = document.getElementById("oh-result-count");
    function filter(updateUrl = true) {
      const terms = query.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      let visible = 0;
      rows.forEach((row) => {
        const show = (category === "all" || row.dataset.category === category) &&
          (access.value === "all" || row.dataset.access === access.value) && terms.every((word) => row.dataset.search.includes(word));
        row.hidden = !show; if (show) visible++;
      });
      buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.category === category)));
      count.textContent = `Showing ${visible} of ${rows.length} components`;
      noResults.hidden = visible !== 0;
      reset.hidden = category === "all" && access.value === "all" && !query.value;
      if (updateUrl && window.location.protocol !== "file:") {
        const url = new URL(window.location.href); url.searchParams.delete("q"); url.searchParams.delete("category"); url.searchParams.delete("access");
        if (query.value.trim()) url.searchParams.set("q", query.value.trim());
        if (category !== "all") url.searchParams.set("category", category);
        if (access.value !== "all") url.searchParams.set("access", access.value);
        window.history.replaceState(null, "", url);
      }
    }
    buttons.forEach((button) => button.addEventListener("click", () => { category = button.dataset.category; filter(); }));
    query.addEventListener("input", () => filter()); access.addEventListener("change", () => filter());
    const clear = () => { category = "all"; query.value = ""; access.value = "all"; filter(); query.focus(); };
    reset.addEventListener("click", clear);
    document.querySelectorAll("[data-reset-catalogue]").forEach((button) => button.addEventListener("click", clear));
    document.addEventListener("keydown", (event) => {
      const tag = document.activeElement?.tagName;
      if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(tag)) { event.preventDefault(); query.focus(); }
    });
    filter(false);
    if (window.location.hash.startsWith("#model-")) {
      const row = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
      if (row?.classList.contains("oh-model-row")) { row.open = true; if (row.hidden) clear(); row.scrollIntoView({block: "start"}); }
    }
  });
})();
