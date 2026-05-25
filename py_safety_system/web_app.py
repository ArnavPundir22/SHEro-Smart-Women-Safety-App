from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safety-secret!'
# Allow all origins so Ngrok connections aren't blocked
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
SENDER_EMAIL = "arnavp128@gmail.com"
SENDER_PASSWORD = "pshk aoim hjde ydol"
EMERGENCY_EMAIL = "cu240251013@coeruniversity.ac.in"
PUBLIC_STREAM_URL = "https://f555-2409-40d2-3055-eaa1-200e-387-c35c-26a1.ngrok-free.app"

alert_sent = False

@app.route('/')
def index():
    # The client/phone interface
    return render_template('index.html')

@app.route('/view')
def view():
    # The viewer interface for the emergency contact
    return render_template('view.html')

@socketio.on('trigger_alert')
def handle_alert(data):
    global alert_sent
    if not alert_sent:
        print("🚨 Alert received from phone!")
        lat = data.get('lat')
        lng = data.get('lng')
        
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        print(f"Location: {maps_link}")
        
        # Send Email
        try:
            msg = EmailMessage()
            msg.set_content(f"Emergency Triggered!\n\nLocation: {maps_link}\nLive Stream: {PUBLIC_STREAM_URL}/view")
            msg['Subject'] = '🚨 EMERGENCY ALERT: HELP NEEDED'
            msg['From'] = SENDER_EMAIL
            msg['To'] = EMERGENCY_EMAIL

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
            print("✅ Email Alert sent!")
            alert_sent = True
        except Exception as e:
            print("❌ Email error:", e)

@socketio.on('video_frame')
def handle_frame(data):
    # Broadcast the base64 jpeg to anyone viewing the stream
    emit('stream_frame', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    print(f"Starting Web App Server...")
    print(f"Open your phone browser to: {PUBLIC_STREAM_URL}")
    socketio.run(app, host='0.0.0.0', port=5000)
