# 🌐 GeoTrack — Location Intelligence Platform

![GeoTrack](https://img.shields.io/badge/GeoTrack-v2.0-00f5ff?style=for-the-badge&logo=googlemaps)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-Educational_Only-ff3c6e?style=for-the-badge)

> ⚠️ **ETHICAL USE ONLY** — This tool is built strictly for cybersecurity education, OSINT research, and ethical demonstrations. Unauthorized tracking is illegal. Always obtain explicit consent.

---

## 🔗 Live Demo

| | Link |
|---|---|
| 🌐 **Dashboard** | [https://ge0track.netlify.app](https://ge0track.netlify.app) |
| ⚙️ **Backend API** | [https://weatherforecast-live.up.railway.app](https://weatherforecast-live.up.railway.app) |
| 🌤️ **Fake Weather Page** | [https://weatherforecast-live.up.railway.app/forecast/world](https://weatherforecast-live.up.railway.app/forecast/world) |

---

## 📸 Features

| Feature | Description |
|---|---|
| 🗺️ **Map Tracker** | GPS + coordinate-based location mapping with reverse geocoding |
| 🔗 **Fake Link** | Social engineering simulation page with GPS + IP capture |
| 🌐 **IP Lookup** | Full IP intelligence — city, ISP, timezone, coordinates |
| 📡 **Capture Log** | Live capture dashboard with auto-refresh |
| 🌤️ **Fake Weather Page** | Convincing decoy page that silently captures GPS/IP location |
| 🔐 **Session Tokens** | Private captures — only you can see your data |

---

## 🗂️ Project Structure

```
GeoTrack/
├── index.html       ← Frontend dashboard (single file, all pages)
├── server.py        ← Flask backend (API + fake weather page)
├── requirements.txt ← Python dependencies
└── README.md
```

---

## ⚙️ Local Setup (Run on Your PC)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/harsh160311/Geo-Track
cd Geo-Track
```

### Step 2 — Install Dependencies

```bash
pip install flask flask-cors requests gunicorn
```

### Step 3 — Run the Server

```bash
python server.py
```

### Step 4 — Open the Dashboard

```
http://localhost:5000
```

---

## ☁️ Deployment

| Layer | Platform | URL |
|---|---|---|
| **Frontend** | Netlify | https://ge0track.netlify.app |
| **Backend** | Railway | https://weatherforecast-live.up.railway.app |

### Deploy Backend (Railway)

1. Push code to GitHub
2. Connect repo on [railway.app](https://railway.app)
3. Set **Start Command:** `gunicorn server:app`
4. Railway auto-deploys on every push ✅

### Deploy Frontend (Netlify)

1. Go to [netlify.app](https://netlify.app)
2. Drag & drop `index.html`
3. Done ✅

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the main dashboard |
| `/forecast/world` | GET | Fake weather page (capture trigger) |
| `/api/ip` | GET | Returns caller's IP info |
| `/api/ip/<ip>` | GET | Lookup any IP address |
| `/api/reverse?lat=&lon=` | GET | Reverse geocode coordinates |
| `/api/session` | GET | Create private session token |
| `/api/capture` | POST | Save a captured location |
| `/api/captures?token=` | GET | Get your session's captures |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Cyberpunk UI), Vanilla JS |
| **Maps** | Leaflet.js + OpenStreetMap |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Geocoding** | Nominatim (OpenStreetMap) |
| **IP Intelligence** | ip-api.com |
| **Deployment** | Railway (backend) + Netlify (frontend) |

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

## 👨‍💻 Author

**Harsh** — Sirsa, Haryana, India  
Built with ❤️ for ethical cybersecurity education.

---

*GeoTrack v2.0 © 2026 — Educational Use Only*
