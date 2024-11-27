import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import os
import time
import pickle



if __name__ == "__main__":
    with open("encodings.pickle", "rb") as f:
        data = pickle.loads(f.read())
else:
    from django.conf import settings
    BASE_DIR = settings.BASE_DIR
    with open(os.path.join(BASE_DIR,"recognition_app", "encodings.pickle"), "rb") as f:
        data = pickle.loads(f.read())

known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))

# Initialize variables
cv_scaler = 4  # this has to be a whole number
face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0

# Function to log recognized names in a file
def log_recognized_name(name, log_file="recognized_faces.txt"):
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            pass  # Create an empty file if it doesn't exist
    with open(log_file, "a") as f:
        f.write(f"{name}\n")

# Process a frame to detect faces
def process_frame(frame):
    global face_locations, face_encodings, face_names
    unknown_detected = False
    # Resize frame for faster processing
    resized_frame = cv2.resize(frame, (0, 0), fx=(1 / cv_scaler), fy=(1 / cv_scaler))
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model="large")

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Find the closest known face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        face_names.append(name)

        # Log recognized name if not "Unknown"
        if name != "Unknown":
            log_recognized_name(name)

        if name == "Unknown":
            unknown_detected = True

    # If unknown face is detected, flash red
    if unknown_detected:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
        alpha = 0.4  # Transparency factor
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    return frame

# Draw results on the frame
def draw_results(frame):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale face locations back to original size
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)

        # Draw a label with the name below the face
        cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)

    return frame

# Calculate FPS
def calculate_fps():
    global frame_count, start_time, fps
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    return fps


def video_stream():
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

if __name__ == "__main__":
    picam2.start()
    while True:
        # Capture a frame from camera
        frame = picam2.capture_array()

        # Process the frame
        processed_frame = process_frame(frame)

        # Draw results on the processed frame
        display_frame = draw_results(processed_frame)

        # Calculate and display FPS
        current_fps = calculate_fps()
        cv2.putText(
            display_frame,
            f"FPS: {current_fps:.1f}",
            (display_frame.shape[1] - 150, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        # Display the video feed
        cv2.imshow("Video", display_frame)

        # Break the loop and stop the script if 'q' is pressed
        if cv2.waitKey(1) == ord("q"):
            break

        cv2.destroyAllWindows()
        picam2.stop()