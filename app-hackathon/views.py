from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2
from picamera2 import Picamera2  
from recognition_app.facial_recognition import process_frame, draw_results, calculate_fps

def video_page(request):
    return render(request, 'video_display.html')

def video_stream():
    """Stream video frames with facial recognition."""

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()

    try:
        while True:
            frame = picam2.capture_array()
            processed_frame = process_frame(frame)
            display_frame = draw_results(processed_frame)
            current_fps = calculate_fps()
            cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Encode frame as JPEG
            _, jpeg = cv2.imencode('.jpg', display_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    finally:
        picam2.stop()

# View pentru streaming
def video_feed(request):
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')