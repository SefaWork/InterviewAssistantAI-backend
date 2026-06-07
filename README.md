# InterviewAssistantAI - Backend

This project contains the backend architecture of an AI-powered interview simulation application. The system analyzes interview performance by performing real-time emotion recognition and eye contact tracking using candidate camera feeds.

## Features

* **Real-Time Data Streaming:** Image frames are received and processed asynchronously via Django Channels (WebSockets) instead of standard HTTP requests.
* **Emotion Recognition (FER):** Real-time emotion detection is performed using a lightweight MobileNetV2 model trained with TensorFlow/Keras.
* **Eye Tracking:** Iris position is calculated using Google Mediapipe Face Mesh to measure the candidate's eye contact ratio with the screen/camera.
* **Singleton Model Management:** Machine learning models are loaded into memory (RAM) only once when the server starts, preventing model reloading delays on every request.
* **Asynchronous Task Management:** Heavy image processing and model prediction tasks (synchronous) are executed on separate workers using `sync_to_async` to prevent blocking the main WebSocket loop.

## Technologies

* **Web Framework:** Django, Django REST Framework (DRF)
* **WebSocket:** Django Channels, Daphne
* **AI & Image Processing:** TensorFlow, OpenCV, Google Mediapipe, NumPy
* **Database:** SQLite3
* **Authentication:** JWT (JSON Web Tokens)

## Installation

Follow the steps below to run the project in your local environment.

**1. Clone the repository:**
```bash
git clone [https://github.com/SefaWork/InterviewAssistantAI-backend.git](https://github.com/SefaWork/InterviewAssistantAI-backend.git)
cd InterviewAssistantAI-backend
```

**2. Create and activate a virtual environment:**
```bash
python -m venv venv
# For Windows:
venv\Scripts\activate
# For MacOS/Linux:
source venv/bin/activate
```

**3. Install the required packages:**
```bash
pip install -r requirements.txt
```

**4. Apply database migrations:**
```bash
python manage.py migrate
```

**5. Start the server:**
```bash
daphne -p 8000 core.asgi:application
```

## Data Output Format

The system returns data in the following JSON format for each processed frame via `consumers.py`:

```json
{
    "type": "result",
    "data": {
        "face_detected": true,
        "face_count": 1,
        "eye_contact_score": 100,
        "emotion": "happy",
        "emotion_confidence": 98.5
    }
}
```
