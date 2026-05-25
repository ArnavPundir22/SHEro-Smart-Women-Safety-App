# SHEro Shield - Smart Women Safety App

SHEro Shield is a voice-activated emergency alert system designed to protect women. The project now features a robust **Mobile-First Python Web Application** that captures a live feed from a smartphone's camera, grabs precise GPS coordinates, and instantly emails emergency contacts.

## 🚀 Features

- **Voice Triggering:** Continuously listens for the hotword **"help"**. If said 3 times, the emergency protocol is automatically triggered.
- **Location Tracking:** Retrieves precise GPS coordinates using the phone's native geolocation API.
- **Camera Casting:** Captures and streams live video from the phone's cameras directly to an emergency viewer dashboard.
- **Instant Alerts:** Sends an immediate SOS email to the configured emergency contact, containing a Google Maps location link and a secure link to watch the live camera stream.

---

## 🛠️ Python Web App (Mobile-First System)

The new Python Web App turns any smartphone into a smart emergency device. The backend is hosted on your computer (via Flask and Socket.IO), while the client runs securely on your phone's browser.

### 1. Installation

Navigate to the project directory and set up a virtual environment:

```bash
cd Smart-Women-Safety-App
python3 -m venv venv
source venv/bin/activate
pip install -r py_safety_system/requirements.txt
```

### 2. Configuration

Open `py_safety_system/web_app.py` and configure the following variables at the top of the file:

- `SENDER_EMAIL`: The Gmail address sending the alerts.
- `SENDER_PASSWORD`: Your Gmail App Password (NOT your regular password).
- `EMERGENCY_EMAIL`: The email address of the person who should receive the SOS.
- `PUBLIC_STREAM_URL`: Your secure Ngrok HTTPS link.

### 3. Running the Server with Ngrok

Because modern phones strictly require `https` for camera and microphone access, you must use **Ngrok** to expose the local server securely.

1. Open a terminal and start Ngrok:
   ```bash
   ngrok http 5000
   ```
2. Copy the generated `https://` link and paste it into `PUBLIC_STREAM_URL` inside `web_app.py`.
3. In a second terminal, start the Python web server:
   ```bash
   source venv/bin/activate
   python py_safety_system/web_app.py
   ```

### 4. How to Use on Your Phone

1. Open your phone's browser (Safari/Chrome) and visit your secure Ngrok URL.
2. Grant permissions for **Microphone**, **Camera**, and **Location**.
3. Tap **Start Monitoring**.
4. Say **"help"** three times.
5. The system will trigger the alert, start broadcasting your cameras, and instantly send an email to your emergency contact!

---

## 📁 Original Node.js System (Legacy)

The repository also includes the original Node.js application.

**To run the legacy app:**
```bash
npm install
npm start
```
*Note: The legacy version uses CSV files for local storage and runs natively on the desktop without mobile-first camera streaming.*