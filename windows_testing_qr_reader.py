import cv2
from pyzbar import pyzbar
import numpy as np

def decode_qr(frame):
    # Find QR codes in the frame
    decoded_objects = pyzbar.decode(frame)
    for obj in decoded_objects:
        # Draw rectangle around the QR code
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = points
        n = len(hull)
        for j in range(0, n):
            cv2.line(frame, hull[j], hull[(j + 1) % n], (0, 255, 0), 3)

        # Display the decoded data
        print(f"Decoded Data: {obj.data.decode('utf-8')}")
        x, y, w, h = obj.rect
        cv2.putText(frame, obj.data.decode('utf-8'), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def main():
    # Initialize the webcam
    cap = cv2.VideoCapture(1)
    focus = 255  # min: 0, max: 255, increment:5
    cap.set(28, focus) 

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        # Decode QR codes in the frame
        frame = decode_qr(frame)

        # Display the resulting frame
        cv2.imshow('QR Code Scanner', frame)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
