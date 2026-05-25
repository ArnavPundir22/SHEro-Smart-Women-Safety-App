import os
import time
import threading
import cv2
import geocoder
import speech_recognition as sr
from flask import Flask, Response, render_template_string
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
HOTWORD = "help"
TRIGGER_COUNT = 3

# Email Config
SENDER_EMAIL = "arnavp128@gmail.com"
SENDER_PASSWORD = "pshk aoim hjde ydol" # Use App Password for Gmail
EMERGENCY_EMAIL = "cu240251013@coeruniversity.ac.in"

# Ngrok Public URL (Optional: replace with your ngrok url to send clickable live stream link)
PUBLIC_STREAM_URL = "https://f555-2409-40d2-3055-eaa1-200e-387-c35c-26a1.ngrok-free.app"

# Globals
alert_triggered = False
help_count = 0
camera_0 = None
camera_1 = None

# ==========================================
# CAMERA STREAMING (Flask)
# ==========================================
def init_cameras():
    global camera_0, camera_1
    camera_0 = cv2.VideoCapture(0) # Front cam (default)
    camera_1 = cv2.VideoCapture(1) # Back cam (if available)

def generate_frames(cam_idx):
    cam = camera_0 if cam_idx == 0 else camera_1
    while True:
        if cam is None or not cam.isOpened():
            # Yield a blank frame or break
            break
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/0')
def video_feed_0():
    return Response(generate_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed/1')
def video_feed_1():
    return Response(generate_frames(1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    html = """
    <html>
    <head><title>Emergency Stream</title></head>
    <body style="text-align: center; font-family: Arial; background-color: #fce4e4;">
        <h1 style="color: red;">🚨 LIVE EMERGENCY STREAM 🚨</h1>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div>
                <h3>Camera 0 (Front)</h3>
                <img src="/video_feed/0" width="400" style="border: 4px solid red; border-radius: 8px;"/>
            </div>
            <div>
                <h3>Camera 1 (Back)</h3>
                <img src="/video_feed/1" width="400" style="border: 4px solid red; border-radius: 8px;"/>
            </div>
        </div>
        <p>Live feed activated due to emergency trigger.</p>
    </body>
    </html>
    """
    return render_template_string(html)

def start_flask():
    print(f"🟢 Starting Live Camera Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# ==========================================
# ALERTS & LOCATION
# ==========================================
def get_location():
    try:
        g = geocoder.ip('me') # IP based geolocation
        if g.latlng:
            lat, lng = g.latlng
            return f"https://www.google.com/maps?q={lat},{lng}", g.city
    except Exception as e:
        print("Location error:", e)
    return "Location unavailable", "Unknown"

def send_alerts(loc_link, city):
    # Send Email
    try:
        if SENDER_EMAIL != "your_email@gmail.com":
            msg = EmailMessage()
            msg.set_content(f"Emergency Triggered!\n\nLocation: {loc_link}\nLive Stream: {PUBLIC_STREAM_URL}")
            msg['Subject'] = '🚨 EMERGENCY ALERT: HELP NEEDED'
            msg['From'] = SENDER_EMAIL
            msg['To'] = EMERGENCY_EMAIL

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
            print("✅ Email Alert sent!")
        else:
            print("⚠️ Email not configured. Skipping Email.")
    except Exception as e:
        print("❌ Email error:", e)

def trigger_emergency():
    global alert_triggered
    if alert_triggered: return
    alert_triggered = True
    print("\n" + "="*40)
    print("🚨 !!! EMERGENCY TRIGGERED !!! 🚨")
    print("="*40 + "\n")
    
    print("📍 Fetching location...")
    loc_link, city = get_location()
    print(f"Location found: {loc_link}")
    
    print("📷 Initializing cameras for casting...")
    init_cameras()
    
    print("🌐 Starting live stream server...")
    threading.Thread(target=start_flask, daemon=True).start()
    
    print("✉️ Sending emergency notifications...")
    send_alerts(loc_link, city)

# ==========================================
# VOICE RECOGNITION (Hotword Detection)
# ==========================================
def listen_loop():
    global help_count
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        print("🔄 Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print(f"🎤 Listening for '{HOTWORD}'... (Say it 3 times to trigger)")
        
        while not alert_triggered:
            try:
                # Listen continuously
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                text = recognizer.recognize_google(audio).lower()
                print(f"🗣️ Heard: '{text}'")
                
                if HOTWORD in text:
                    help_count += 1
                    print(f"⚠️ Hotword detected! ({help_count}/{TRIGGER_COUNT})")
                    if help_count >= TRIGGER_COUNT:
                        trigger_emergency()
            except sr.WaitTimeoutError:
                # Normal timeout, just keep listening
                pass
            except sr.UnknownValueError:
                # Unrecognizable audio
                pass
            except Exception as e:
                pass

if __name__ == "__main__":
    try:
        listen_loop()
        # Keep the main thread alive if alert is triggered so the stream server keeps running
        if alert_triggered:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
        if camera_0: camera_0.release()
        if camera_1: camera_1.release()
