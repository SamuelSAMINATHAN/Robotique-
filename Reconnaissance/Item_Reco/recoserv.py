from flask import Flask, Response, render_template_string
import cv2
# from item_learning import page_closed

page_closed = False


app = Flask(__name__)

# Open webcam (0 is usually default camera)
camera = cv2.VideoCapture(0)

def generate_frames():
    while not page_closed:
        success, frame = camera.read()
        if not success:
            break

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Use multipart format to push frames
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()
    page_closed = True

@app.route('/')
def index():
    # Simple HTML to show the stream
    return render_template_string('''
        <html>
        <head><title>Live Stream</title></head>
        <script>
    window.onbeforeunload = function () {
    navigator.sendBeacon('/closed');
    };
</script>

        <body>
            <h1>Live Camera Feed</h1>
            <img src="{{ url_for('video') }}">
        </body>
        </html>
    ''')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
