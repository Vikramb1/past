import cv2

def open_first_camera(max_idx=6):
    for i in range(max_idx):
        cap = cv2.VideoCapture(i, cv2.CAP_ANY)
        if cap.isOpened() and i not in [0,1]:
            print(f"Opened camera index {i}")
            return cap
    raise RuntimeError("No camera device opened. Is OBS Virtual Camera running?")

cap = open_first_camera()

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("OBS Virtual Cam", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
