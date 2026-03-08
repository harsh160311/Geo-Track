# 🌐 GeoTrack — Location Intelligence Platform

![GeoTrack](https://img.shields.io/badge/GeoTrack-v2.0-00f5ff?style=for-the-badge&logo=googlemaps)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-Educational_Only-ff3c6e?style=for-the-badge)

> ⚠️ **ETHICAL USE ONLY** — This tool is built strictly for cybersecurity education, OSINT research, and ethical demonstrations. Unauthorized tracking is illegal. Always obtain explicit consent.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🗺️ **Map Tracker** | GPS + coordinate-based location mapping with reverse geocoding |
| 🔗 **Fake Link** | Ngrok-powered social engineering simulation page |
| 🌐 **IP Lookup** | Full IP intelligence — city, ISP, timezone, coordinates |
| 📡 **Capture Log** | Live capture dashboard with auto-refresh every 5 seconds |
| 🌤️ **Fake Weather Page** | Convincing decoy page that silently captures GPS/IP location |

---

## 🗂️ Project Structure

```
GeoTrack/
├── index.html       ← Frontend dashboard (single file, all pages)
├── server.py        ← Flask backend (API + ngrok + fake weather page)
├── requirements.txt ← Python dependencies
└── README.md
```

---

## ⚙️ Local Setup (Run on Your PC)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/GeoTrack.git
cd GeoTrack
```

### Step 2 — Install Dependencies

```bash
pip install flask flask-cors pyngrok requests
```

### Step 3 — Run the Server

```bash
python server.py
```

### Step 4 — Open the Dashboard

```
http://localhost:5000
```

The terminal will also print your **Ngrok public URL** automatically:

```
=======================================================
  NGROK URL   : https://xxxx-xx-xx-xxx.ngrok-free.app
  Fake Weather: https://xxxx-xx-xx-xxx.ngrok-free.app/weather
=======================================================
```

---

## 🌍 Live Deployment Guide (Free — Render.com)

> **Problem:** Flask backend needs a server to run. GitHub Pages only hosts static HTML — it cannot run Python.  
> **Solution:** Deploy backend on **Render** (free) and update the frontend URL.

---

### 🔧 Step 1 — Prepare Files for Deployment

Create a `requirements.txt` file in your project folder:

```
flask
flask-cors
requests
gunicorn
```

> ⚠️ Do **NOT** include `pyngrok` in requirements.txt for deployment — ngrok won't work on cloud servers. The server handles this gracefully already.

---

### 🔧 Step 2 — Update `server.py` for Production

Open `server.py` and make sure the last line looks like this (it already does):

```python
app.run(host="0.0.0.0", port=5000, debug=False)
```

Render uses **Gunicorn** to run the app, so this line won't even be used in production — but keep it for local use.

---

### 🔧 Step 3 — Update Frontend URL in `index.html`

Open `index.html` and find this line near the top of the `<script>` section:

```javascript
var SRV = 'http://localhost:5000';
```

Change it to your **Render backend URL** (you'll get this after deploying):

```javascript
var SRV = 'https://your-app-name.onrender.com';
```

---

### 🔧 Step 4 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — GeoTrack v2.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/GeoTrack.git
git push -u origin main
```

---

### 🔧 Step 5 — Deploy Backend on Render

1. Go to **[render.com](https://render.com)** → Sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub account** → Select the **GeoTrack** repo
4. Fill in the settings:

| Setting | Value |
|---|---|
| **Name** | `geotrack-backend` (any name) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn server:app` |
| **Instance Type** | `Free` |

5. Click **"Create Web Service"**
6. Wait ~2 minutes for the build to finish
7. Copy your live URL — it looks like: `https://geotrack-backend.onrender.com`

---

### 🔧 Step 6 — Deploy Frontend on GitHub Pages

Since `index.html` is now pointing to your Render backend, you can host the frontend on GitHub Pages for free:

1. Go to your GitHub repo → **Settings**
2. Scroll to **"Pages"** section
3. Under **Branch**, select `main` → folder `/root`
4. Click **Save**
5. Your frontend will be live at:  
   `https://YOUR_USERNAME.github.io/GeoTrack/`

---

## 🔑 Optional — Ngrok Auth Token (for local use)

If ngrok shows errors locally, get a free token from [ngrok.com](https://ngrok.com) and add it in `server.py`:

```python
# Find this line in start_ngrok() function:
# conf.get_default().auth_token = "YOUR_NGROK_TOKEN"

# Remove the # and paste your token:
conf.get_default().auth_token = "2abc123xyz_yourActualTokenHere"
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the main dashboard |
| `/weather` | GET | Fake weather page (capture trigger) |
| `/api/ip` | GET | Returns caller's IP info |
| `/api/ip/<ip>` | GET | Lookup any IP address |
| `/api/reverse?lat=&lon=` | GET | Reverse geocode coordinates |
| `/api/capture` | POST | Save a captured location |
| `/api/captures` | GET | Get all captured locations |
| `/api/ngrok-url` | GET | Get current ngrok tunnel URL |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Cyberpunk UI), Vanilla JS |
| **Maps** | Leaflet.js + OpenStreetMap |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Geocoding** | Nominatim (OpenStreetMap) |
| **IP Intelligence** | ip-api.com |
| **Tunneling** | ngrok / pyngrok |
| **Deployment** | Render (backend) + GitHub Pages (frontend) |

---

## ⚠️ Legal Disclaimer

This project is created **strictly for educational purposes**:

- ✅ Cybersecurity awareness demonstrations
- ✅ OSINT research in controlled environments  
- ✅ Personal learning and ethical hacking practice
- ❌ Tracking individuals without consent
- ❌ Any unauthorized surveillance
- ❌ Illegal use of any kind

**Misuse of this tool is illegal and strictly prohibited.**

---

## 👩‍💻 Author

**Saroj Rani** — Sirsa, Haryana, India  
Built with ❤️ for ethical cybersecurity education.

---

*GeoTrack v2.0 © 2026 — Educational Use Only*
