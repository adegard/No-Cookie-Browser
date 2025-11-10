import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

class NoCookieBrowser(Gtk.Window):
    def __init__(self):
        super().__init__(title="No-Cookie Browser")
        self.set_default_size(1000, 700)

        # Optional dark mode
        Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)

        self.bookmarks = []
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        # Header bar
        header = Gtk.HeaderBar(title="No-Cookie Browser")
        header.set_show_close_button(True)
        self.set_titlebar(header)

        new_tab_btn = Gtk.Button(label="New Tab")
        new_tab_btn.connect("clicked", lambda _: self.add_tab("https://duckduckgo.com"))
        header.pack_start(new_tab_btn)

        bookmark_btn = Gtk.Button(label="★")
        bookmark_btn.connect("clicked", self.show_bookmarks)
        header.pack_end(bookmark_btn)

        self.add_tab("https://duckduckgo.com")

    def add_tab(self, url):
        # Ephemeral context: no cookies, cache, localStorage, IndexedDB
        context = WebKit2.WebContext.new_ephemeral()

        # Block downloads at the context level
        context.connect("download-started", lambda ctx, dl: dl.cancel())

        # Create WebView with this context
        webview = WebKit2.WebView.new_with_context(context)

        # Inject a basic ad-blocker via the view's user content manager
        ucm = webview.get_user_content_manager()
        ad_script = """
            const blocked = ['doubleclick.net', 'googlesyndication.com', 'adsafeprotected.com'];
            blocked.forEach(domain => {
                document.querySelectorAll(`[src*="${domain}"], [href*="${domain}"]`).forEach(el => {
                    if (el.parentNode) el.parentNode.removeChild(el);
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

        # Address bar
        entry = Gtk.Entry()
        entry.set_text(url)
        entry.connect("activate", lambda w: self.navigate(webview, w.get_text()))

        # Navigation buttons
        back_btn = Gtk.Button(label="←")
        back_btn.connect("clicked", lambda _: webview.go_back())
        fwd_btn = Gtk.Button(label="→")
        fwd_btn.connect("clicked", lambda _: webview.go_forward())
        reload_btn = Gtk.Button(label="⟳")
        reload_btn.connect("clicked", lambda _: webview.reload())

        # Bookmark button for this tab
        tab_bookmark_btn = Gtk.Button(label="★")
        tab_bookmark_btn.connect("clicked", lambda _: self.add_bookmark(webview.get_uri()))

        nav_box = Gtk.Box(spacing=5)
        nav_box.pack_start(back_btn, False, False, 0)
        nav_box.pack_start(fwd_btn, False, False, 0)
        nav_box.pack_start(reload_btn, False, False, 0)
        nav_box.pack_start(entry, True, True, 0)
        nav_box.pack_end(tab_bookmark_btn, False, False, 0)

        # Tab container
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        container.pack_start(nav_box, False, False, 0)
        container.pack_start(webview, True, True, 0)

        # Tab label updates with page title
        tab_label = Gtk.Label(label="Loading…")
        self.notebook.append_page(container, tab_label)
        self.notebook.set_tab_reorderable(container, True)

        webview.connect("notify::title", lambda view, _: tab_label.set_text(view.get_title() or "Tab"))

        # Load initial URL
        self.navigate(webview, url)

        self.show_all()

    def navigate(self, webview, url):
        # Normalize URL
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webview.load_uri(url)

    def add_bookmark(self, url):
        if url and url not in self.bookmarks:
            self.bookmarks.append(url)

    def show_bookmarks(self, _):
        dialog = Gtk.Dialog(title="Bookmarks", transient_for=self, flags=0)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        box = dialog.get_content_area()

        if not self.bookmarks:
            box.add(Gtk.Label(label="No bookmarks yet."))
        else:
            for url in self.bookmarks:
                btn = Gtk.Button(label=url)
                btn.connect("clicked", lambda _, u=url: self.add_tab(u))
                box.add(btn)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    win = NoCookieBrowser()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
