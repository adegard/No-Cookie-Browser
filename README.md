# No-Cookie Browser 🕶️

A lightweight Linux desktop web browser built with **Python + GTK + WebKitGTK**, designed for privacy:
- 🚫 No cookies (ephemeral context)
- 🗂️ Tabbed browsing
- ⭐ In-memory bookmarks
- ⛔ Download blocking
- 🧹 Basic ad filtering
- 🌙 Optional dark mode

## ✨ Features
- Ephemeral browsing context (no cookies, cache, localStorage, or IndexedDB)
- Multiple tabs with dynamic titles
- Address bar with navigation buttons
- Bookmark manager (in-memory)
- JavaScript ad-blocker for common ad domains
- Dark mode toggle via GTK settings

## 📦 Requirements
Install dependencies (Debian/Ubuntu):

```bash
sudo apt install python3-gi gir1.2-webkit2-4.0 gir1.2-gtk-3.0
