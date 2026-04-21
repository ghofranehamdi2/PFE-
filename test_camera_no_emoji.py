import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not found or busy.")
else:
    print("Camera found!")
    ret, frame = cap.read()
    if ret:
        print(f"Captured frame of size: {frame.shape}")
    else:
        print("Could not read frame.")
cap.release()
