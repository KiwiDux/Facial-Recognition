import cv2


class Camera:
    def capture_when_face_detected(self):
        cam = cv2.VideoCapture(0)   # 0 = default camera
        face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        
        if not cam.isOpened():
            print("Failed to open camera.")
            return

        try:
            while True:
                ret, frame = cam.read()
                if not ret:
                    print("Failed to capture image.")
                    break

                grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_detector.detectMultiScale(
                    grayscale_frame,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                )

                for x, y, width, height in faces:
                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + width, y + height),
                        (0, 255, 0),
                        2,
                    )

                cv2.imshow("Camera", frame)

                if len(faces) > 0:
                    cv2.imwrite("captured_image.png", frame)
                    print("Face detected. Image saved as captured_image.png.")
                    break

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            cam.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    Camera().capture_when_face_detected()
