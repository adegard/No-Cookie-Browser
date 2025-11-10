import gi, os, json
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

APP_NAME = "nocookie_browser"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", APP_NAME)
BOOKMARKS_PATH = os.path.join(CONFIG_DIR, "bookmarks.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "homepage": "https://example.com",
    "dark_mode": True
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
        with open(path) as f:
            return json.load(f)
    except Exception:
        return fallback

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed to save", path, e)

class NoCookieBrowser(Gtk.Window):
    def __init__(self):
        super().__init__(title="No-Cookie Browser")
        ensure_paths()
        self.settings = load_json(SETTINGS_PATH, DEFAULT_SETTINGS.copy())
        self.bookmarks = load_json(BOOKMARKS_PATH, [])
        self.set_default_size(1000, 700)

        # Dark mode
        Gtk.Settings.get_default().set_property(
            "gtk-application-prefer-dark-theme",
            bool(self.settings.get("dark_mode", True))
        )

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # Header bar
        header = Gtk.HeaderBar(title="No-Cookie Browser")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        new_tab_btn = Gtk.Button(label="New Tab")
        new_tab_btn.connect("clicked", lambda _: self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"])))
        header.pack_start(new_tab_btn)

        bookmarks_btn = Gtk.Button(label="Bookmarks")
        bookmarks_btn.connect("clicked", self.show_bookmarks)
        header.pack_start(bookmarks_btn)

        settings_btn = Gtk.Button(label="Settings")
        settings_btn.connect("clicked", self.show_settings)
        header.pack_end(settings_btn)

        # Initial tab
        self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))

    def add_tab(self, url):
        # Ephemeral context: no cookies, cache, storage
        context = WebKit2.WebContext.new_ephemeral()
        context.connect("download-started", lambda ctx, dl: dl.cancel())

        webview = WebKit2.WebView.new_with_context(context)

        # Inject basic ad-blocker
        ucm = webview.get_user_content_manager()
        ad_script = """
            const blocked = ['doubleclick.net','googlesyndication.com','adsafeprotected.com'];
            blocked.forEach(domain => {
              document.querySelectorAll(`[src*="${domain}"],[href*="${domain}"]`).forEach(el => {
                el.remove();
              });
            });
        """
        script = WebKit2.UserScript.new(
            ad_script,
            WebKit2.UserContentInjectedFrames.ALL_FRAMES,
            WebKit2.UserScriptInjectionTime.START,
            [], []
        )
        ucm.add_script(script)

        # Address bar + navigation
        entry = Gtk.Entry()
        entry.set_text(url)
        entry.connect("activate", lambda w: self.navigate(webview, w.get_text()))

        back_btn = Gtk.Button(label="←")
        back_btn.connect("clicked", lambda _: webview.go_back())
        fwd_btn = Gtk.Button(label="→")
        fwd_btn.connect("clicked", lambda _: webview.go_forward())
        reload_btn = Gtk.Button(label="⟳")
        reload_btn.connect("clicked", lambda _: webview.reload())

        tab_bookmark_btn = Gtk.Button(label="★")
        tab_bookmark_btn.connect("clicked", lambda _: self.add_bookmark(webview.get_uri()))

        nav_box = Gtk.Box(spacing=5)
        nav_box.pack_start(back_btn, False, False, 0)
        nav_box.pack_start(fwd_btn, False, False, 0)
        nav_box.pack_start(reload_btn, False, False, 0)
        nav_box.pack_start(entry, True, True, 0)
        nav_box.pack_end(tab_bookmark_btn, False, False, 0)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        container.pack_start(nav_box, False, False, 0)
        container.pack_start(webview, True, True, 0)

        # Tab label with close button
        tab_label_box = Gtk.Box(spacing=4)
        title_label = Gtk.Label(label="Loading…")
        close_btn = Gtk.Button(label="x")
        close_btn.set_relief(Gtk.ReliefStyle.NONE)
        close_btn.set_focus_on_click(False)
        close_btn.connect("clicked", lambda _: self.close_tab(container))
        tab_label_box.pack_start(title_label, False, False, 0)
        tab_label_box.pack_start(close_btn, False, False, 0)
        tab_label_box.show_all()

        page_num = self.notebook.append_page(container, tab_label_box)
        self.notebook.set_tab_reorderable(container, True)

        webview.connect("notify::title", lambda view, _: title_label.set_text(view.get_title() or "Tab"))

        self.navigate(webview, url)
        self.show_all()
        self.notebook.set_current_page(page_num)

    def close_tab(self, page_widget):
        page_num = self.notebook.page_num(page_widget)
        if page_num != -1:
            self.notebook.remove_page(page_num)
            if self.notebook.get_n_pages() == 0:
                # Open a fresh tab or quit
                self.add_tab(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))

    def navigate(self, webview, url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webview.load_uri(url)

    def add_bookmark(self, url):
        if url and url not in self.bookmarks:
            self.bookmarks.append(url)
            save_json(BOOKMARKS_PATH, self.bookmarks)

    def show_bookmarks(self, _):
        dialog = Gtk.Dialog(title="Bookmarks", transient_for=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.add_button("Clear All", Gtk.ResponseType.APPLY)
        box = dialog.get_content_area()

        if not self.bookmarks:
            box.add(Gtk.Label(label="No bookmarks yet."))
        else:
            for url in self.bookmarks:
                row = Gtk.Box(spacing=6)
                open_btn = Gtk.Button(label="Open")
                open_btn.connect("clicked", lambda _, u=url: self.add_tab(u))
                del_btn = Gtk.Button(label="Delete")
                del_btn.connect("clicked", lambda _, u=url: self.delete_bookmark(u, dialog))
                row.pack_start(Gtk.Label(label=url), True, True, 0)
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
        if url in self.bookmarks:
            self.bookmarks.remove(url)
            save_json(BOOKMARKS_PATH, self.bookmarks)
            dialog.destroy()
            self.show_bookmarks(None)

    def show_settings(self, _):
        dialog = Gtk.Dialog(title="Settings", transient_for=self, flags=0)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.OK)
        box = dialog.get_content_area()

        # Homepage
        home_row = Gtk.Box(spacing=8)
        home_row.pack_start(Gtk.Label(label="Homepage:"), False, False, 0)
        home_entry = Gtk.Entry()
        home_entry.set_text(self.settings.get("homepage", DEFAULT_SETTINGS["homepage"]))
        home_row.pack_start(home_entry, True, True, 0)

        # Dark mode
        dark_row = Gtk.Box(spacing=8)
        dark_mode_switch = Gtk.Switch()
        dark_mode_switch.set_active(bool(self.settings.get("dark_mode", True)))
        dark_row.pack_start(Gtk.Label(label="Dark mode:"), False, False, 0)
        dark_row.pack_start(dark_mode_switch, False, False, 0)

        box.add(home_row)
        box.add(dark_row)

        dialog.show_all()
        resp = dialog.run()
        if resp == Gtk.ResponseType.OK:
            self.settings["homepage"] = home_entry.get_text().strip() or DEFAULT_SETTINGS["homepage"]
            self.settings["dark_mode"] = dark_mode_switch.get_active()
            save_json(SETTINGS_PATH, self.settings)

            Gtk.Settings.get_default().set_property(
                "gtk-application-prefer-dark-theme",
                bool(self.settings["dark_mode"])
            )
        dialog.destroy()

if __name__ == "__main__":
    win = NoCookieBrowser()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
