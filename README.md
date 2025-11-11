# No-Cookie Browser 🕶️

A lightweight Linux desktop web browser built with **Python + GTK + WebKitGTK**, designed for privacy:
- 🚫 No cookies (ephemeral context)
- 🗂️ Tabbed browsing
- ⭐ In-memory bookmarks
- ⛔ Download blocking
- 🧹 Basic ad filtering

## ✨ Features
- Ephemeral browsing context (no cookies, cache, localStorage, or IndexedDB)
- Multiple tabs with dynamic titles
- Address bar with navigation buttons
- Bookmark manager (in-memory)
- JavaScript ad-blocker for common ad domains

## 📦 Requirements
Install dependencies (Debian/Ubuntu):

```bash
sudo apt install python3-gi gir1.2-webkit2-4.0 gir1.2-gtk-3.0
```

📦 Install from .deb package
Install dependencies (if not already installed):

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-webkit2-4.0 gir1.2-gtk-3.0
```
Download and install the .deb package:

```bash
sudo dpkg -i nocookie-browser_0.2.0-1_all.deb
```

Fix missing dependencies (if needed):

```bash
sudo apt --fix-broken install
```

Launch the browser:

```bash
nocookie-browser
```

🧩 Optional: Add to App Menu
To make it appear in your desktop launcher:

Create a .desktop file:

```bash
sudo nano /usr/share/applications/nocookie-browser.desktop
```
Paste this:

```ini
[Desktop Entry]
Name=No-Cookie Browser
Exec=env WEBKIT_DISABLE_DMABUF_RENDERER=1 nocookie-browser
Icon=web-browser
Type=Application
Categories=Network;WebBrowser;
```
Save and make it executable:

```bash
sudo chmod +x /usr/share/applications/nocookie-browser.desktop
```

🧼 Uninstall
```bash
sudo apt remove nocookie-browser
```
