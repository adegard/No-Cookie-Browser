# 🕹️ NoCookie Retro Browser

A lightweight GTK + WebKit2 browser designed for **retro gaming atmosphere** and the **old internet feel of the 90s/early 2000s**.  
It runs in ephemeral mode (no cookies, no cache, no local storage), giving you privacy by default and a nostalgic browsing experience.
![nocookie-browser](screen.png)

---

## ✨ Features

- **Retro 8‑bit style**
  - Pixelated text rendering (blocky fonts, no anti‑aliasing)
  - Pixelated images and videos (same size, crisp edges)
  - Dark CRT‑like backgrounds with forced grey overrides for white/light pages
  - Flat, blocky buttons and inputs — no rounded corners, no glossy effects

- **Privacy first**
  - Ephemeral WebKit context: no cookies, cache, or local storage
  - Blocks sites from forcing fullscreen mode
  - Cancels downloads automatically

- **Classic browsing controls**
  - Tabs with close buttons
  - Back, forward, reload, and bookmark buttons
  - Bookmark manager (add, open, delete, clear)

- **Settings panel**
  - Homepage selection
  - Dark mode toggle
  - Retro style toggle
  - Zoom control (0.5x – 2.0x)
  - Lock window size (prevent sites from resizing your window)

---

## 🚀 Installation

## 📦 Requirements [PYTHON]
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
