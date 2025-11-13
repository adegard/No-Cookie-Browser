#!/usr/bin/env python3
import gi
import os
import json
import sys

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2, GLib

APP_NAME = "nocookie_browser"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)
BOOKMARKS_PATH = os.path.join(CONFIG_DIR, "bookmarks.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "homepage": "https://example.com",
    "dark_mode": True,
    "apply_retro_style": True
}

def ensure_paths():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(BOOKMARKS_PATH):
        with open(BOOKMARKS_PATH, "w") as f:
            json.dump([], f)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(DEFAULT_SETTINGS, f)

def load_json(path, fallback):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return fallback

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed saving", path, e, file=sys.stderr)

# Retro style CSS injected into each page when enabled
RETRO_STYLE_SCRIPT = r"""
(function(){
  try {
    if (document.__retro_style_injected) return;
    const style = document.createElement('style');
    style.id = 'retro-style-inject';
    style.textContent = `
      /* Use a bitmap/pixel font if available; fall back to monospace */
      body, input, textarea, button, select, p, li, span, a {
        font-family: "Press Start 2P", "Pixel 8x8", "Courier New", monospace !important;
        font-size: 13px !important;
        line-height: 1.15 !important;
        color: #e8e8e8 !important;
        text-shadow: 0 0 0 #000, 1px 1px 0 #111 !important;
        letter-spacing: 0.5px !important;
      }

      /* High contrast, desaturated retro palette for backgrounds */
      body, html {
        background-color: #0b0b0b !important;
        color: #e8e8e8 !important;
      }

      /* Pixelate images and videos */
      img, video {
        image-rendering: pixelated !important;
        image-rendering: -webkit-optimize-contrast !important;
        image-rendering: -moz-crisp-edges !important;
        image-rendering: crisp-edges !important;
        filter: contrast(140%) saturate(80%) brightness(105%) !important;
        /* Prefer nearest-neighbor (keep natural size when possible) */
        max-width: none !important;
        max-height: none !important;
        width: auto !important;
        height: auto !important;
      }

      /* Make large images display as blocky thumbnails if constrained by layout */
      img.retro-scale, video.retro-scale {
        transform-origin: top left !important;
        transform: scale(2) !important;
      }

      /* Buttons and inputs with retro look */
      button, input[type="button"], input[type="submit"], a.button {
        border: 2px solid #444 !important;
        background: linear-gradient(#222, #111) !important;
        color: #e8e8e8 !important;
        padding: 6px 10px !important;
        box-shadow: none !important;
      }

      /* Reduce rounded corners */
      * { border-radius: 0 !important; }

      /* Make SVG icons appear more 'blocky' by scaling - best-effort */
      svg { shape-rendering: crispEdges !important; image-rendering: pixelated !important; }

      /* Optional: reduce heavy shadows/blur from sites */
      * { filter: none !important; text-shadow: none !important; box-shadow: none !important; }
    `;
    document.documentElement.appendChild(style);
    document.__retro_style_injected = true;

    // A small helper: add .retro-scale to images that are displayed smaller than their natural size
    function markScaledImages() {
      try {
        document.querySelectorAll('img,video').forEach(el => {
          const w = el.naturalWidth || el.videoWidth || 0;
          const h = el.naturalHeight || el.videoHeight || 0;
          if (w > 0 && h > 0) {
            const displayedW = el.clientWidth || el.width || 0;
            const displayedH = el.clientHeight || el.height || 0;
            // if the image is being downscaled by CSS/layout, apply retro-scale class so nearest-neighbor scaling becomes visible
            if (displayedW < Math.max(1, w) && displayedH < Math.max(1, h)) {
              el.classList.add('retro-scale');
            } else {
              el.classList.remove('retro-scale');
            }
          }
        });
      } catch(e){}
    }

    // Run once and schedule a few short retries for dynamically loaded content
    markScaledImages();
    let tries = 0;
    const t = setInterval(() => {
      tries += 1;
      markScaledImages();
      if (tries >= 6) clearInterval(t);
    }, 400);

  } catch(e){}
})();
"""

class NoCookieBrowser(Gtk.Window):
    def __init__(self):
        super().__init__(title="No-Cookie Browser")
        ensure_paths()
        self.settings = load_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
        self.bookmarks = load_json(BOOKMARKS_PATH, [])
        self.set_default_size(1000, 700)

        try:
            Gtk.Settings.get_default().set_property(
                "gtk-application-prefer-dark-theme",
                bool(self.settings.get("dark_mode", True))
            )
        except Exception:
            pass

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        header = Gtk.HeaderBar(title="No-Cookie Browser")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        header.pack_start(self._make_button("New Tab", lambda w: self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))))
        header.pack_start(self._make_button("Bookmarks", lambda w: self.show_bookmarks()))
        header.pack_end(self._make_button("Settings", lambda w: self.show_settings()))

        # start with initial tab
        self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))

    def _make_button(self, label, callback):
        btn = Gtk.Button(label=label)
        btn.connect("clicked", callback)
        return btn

    def add_tab(self, url):
        context = WebKit2.WebContext.new_ephemeral()
        context.connect("download-started", lambda ctx, dl: dl.cancel())

        webview = WebKit2.WebView.new_with_context(context)
        ucm = webview.get_user_content_manager()

        # Inject retro style if enabled
        if self.settings.get("apply_retro_style", True):
            ucm.add_script(WebKit2.UserScript.new(
                RETRO_STYLE_SCRIPT,
                WebKit2.UserContentInjectedFrames.ALL_FRAMES,
                WebKit2.UserScriptInjectionTime.END,
                [], []
            ))

        # Navigation widgets
        entry = Gtk.Entry()
        entry.set_text(url)
        entry.connect("activate", lambda w: self.navigate(webview, w.get_text()))

        back_btn = self._make_button("←", lambda w: webview.go_back())
        forward_btn = self._make_button("→", lambda w: webview.go_forward())
        reload_btn = self._make_button("⟳", lambda w: webview.reload())
        bookmark_btn = self._make_button("★", lambda w: self.add_bookmark(webview.get_uri() or entry.get_text()))

        nav_box = Gtk.Box(spacing=6)
        nav_box.pack_start(back_btn, False, False, 0)
        nav_box.pack_start(forward_btn, False, False, 0)
        nav_box.pack_start(reload_btn, False, False, 0)
        nav_box.pack_start(entry, True, True, 0)
        nav_box.pack_end(bookmark_btn, False, False, 0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.pack_start(nav_box, False, False, 0)
        container.pack_start(webview, True, True, 0)

        # Tab label with close button
        tab_box = Gtk.Box(spacing=4)
        title_lbl = Gtk.Label(label="Loading…")
        close_btn = Gtk.Button(label="x")
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.set_focus_on_click(False)
        close_btn.connect("clicked", lambda w: self.close_tab(container))
        tab_box.pack_start(title_lbl, False, False, 0)
        tab_box.pack_start(close_btn, False, False, 0)
        tab_box.show_all()

        page_index = self.notebook.append_page(container, tab_box)
        self.notebook.set_tab_reorderable(container, True)

        # Update tab title and address entry
        def on_title_notify(view, prop):
            try:
                t = view.get_title() or view.get_uri() or "Tab"
                title_lbl.set_text(t)
            except Exception:
                pass
        webview.connect("notify::title", on_title_notify)
        webview.connect("notify::uri", lambda v, p: entry.set_text(v.get_uri() or ""))

        self.navigate(webview, url)
        self.show_all()
        self.notebook.set_current_page(page_index)

    def close_tab(self, widget):
        try:
            idx = self.notebook.page_num(widget)
            if idx != -1:
                self.notebook.remove_page(idx)
        except Exception:
            pass
        if self.notebook.get_n_pages() == 0:
            self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))

    def navigate(self, webview, url):
        if not url:
            return
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        try:
            webview.load_uri(url)
        except Exception:
            pass

    def add_bookmark(self, url):
        if not url:
            return
        if url not in self.bookmarks:
            self.bookmarks.append(url)
            save_json(BOOKMARKS_PATH, self.bookmarks)

    def show_bookmarks(self):
        dialog = Gtk.Dialog(title="Bookmarks", transient_for=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.add_button("Clear All", Gtk.ResponseType.APPLY)
        box = dialog.get_content_area()
        if not self.bookmarks:
            box.add(Gtk.Label(label="No bookmarks yet."))
        else:
            for url in list(self.bookmarks):
                row = Gtk.Box(spacing=6)
                lbl = Gtk.Label(label=url, xalign=0)
                open_btn = self._make_button("Open", lambda w, u=url: self.add_tab(u))
                del_btn = self._make_button("Delete", lambda w, u=url, d=dialog: self.delete_bookmark(u, d))
                row.pack_start(lbl, True, True, 0)
                row.pack_end(del_btn, False, False, 0)
                row.pack_end(open_btn, False, False, 0)
                box.add(row)
        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            self.bookmarks = []
            save_json(BOOKMARKS_PATH, self.bookmarks)
        dialog.destroy()

    def delete_bookmark(self, url, dialog):
        try:
            if url in self.bookmarks:
                self.bookmarks.remove(url)
                save_json(BOOKMARKS_PATH, self.bookmarks)
        except Exception:
            pass
        dialog.destroy()
        GLib.idle_add(self.show_bookmarks)

    def show_settings(self):
        dialog = Gtk.Dialog(title="Settings", transient_for=self, flags=0)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.OK)
        box = dialog.get_content_area()

        home_entry = Gtk.Entry()
        home_entry.set_text(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))

        dark_switch = Gtk.Switch()
        dark_switch.set_active(bool(self.settings.get("dark_mode", True)))

        retro_switch = Gtk.Switch()
        retro_switch.set_active(bool(self.settings.get("apply_retro_style", True)))

        for label_text, widget in [("Homepage:", home_entry), ("Dark mode:", dark_switch), ("Retro 8-bit style:", retro_switch)]:
            row = Gtk.Box(spacing=8)
            row.pack_start(Gtk.Label(label=label_text), False, False, 0)
            row.pack_start(widget, True, True, 0)
            box.add(row)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.settings["homepage"] = home_entry.get_text().strip() or DEFAULT_SETTINGS["homepage"]
            self.settings["dark_mode"] = dark_switch.get_active()
            self.settings["apply_retro_style"] = retro_switch.get_active()
            save_json(SETTINGS_PATH, self.settings)
            try:
                Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", bool(self.settings["dark_mode"]))
            except Exception:
                pass
        dialog.destroy()

def main():
    win = NoCookieBrowser()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
