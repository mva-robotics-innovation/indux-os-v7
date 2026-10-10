"""Push real or simulated sensor readings to INDUX-OS.
Usage: python sensor_client.py https://YOUR-BACKEND sensor_id [serial_port]
Serial mode expects one numeric value per line (Arduino/ESP32 Serial.println)."""
import sys, time, random, json, urllib.request
api, sid = sys.argv[1].rstrip("/"), sys.argv[2]
def post(v):
    req = urllib.request.Request(api + "/api/sensor", json.dumps({"sensor": sid, "value": v}).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10).read()
if len(sys.argv) > 3:
    import serial  # pip install pyserial
    s = serial.Serial(sys.argv[3], 9600, timeout=2)
    while True:
        try: post(float(s.readline().decode().strip()))
        except ValueError: pass
else:
    i = 0
    while True:
        post(round(2.1 + random.uniform(-.2, .2) + max(0, i - 40) * .05, 3)); i += 1; time.sleep(1)
