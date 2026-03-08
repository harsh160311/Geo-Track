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
git clone https://github.com/harsh160311/Geo-Track
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

**Harsh** — Sirsa, Haryana, India  
Built with ❤️ for ethical cybersecurity education.

---

*GeoTrack v2.0 © 2026 — Educational Use Only*
