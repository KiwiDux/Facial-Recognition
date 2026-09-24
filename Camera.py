import cv2, os, sys

class Camera:
    def capture_when_face_detected(self):
        cam = cv2.VideoCapture(0)   # 0 = default 
        xml = 'haarcascade_frontalface_default.xml'
        face_detector = cv2.CascadeClassifier(xml)
        file_name = 'captured_image'
        user_image = cv2.imread(file_name)
        
        # Check if the camera opened successfully
        if not cam.isOpened():
            print('Failed to open camera.')
            return

        try:
            while True:
                ret, frame = cam.read()
                if not ret:
                    print('Failed to capture image.')
                    break

                # Gray scale conversion for face detection
                gray_captured = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                faces = face_detector.detectMultiScale(
                    gray_captured,
                    scaleFactor = 1.1,
                    minNeighbors = 3,   # Used when comparing reference image with captured image 'Neighbors' is the number of faces detected.
                    minSize = (50, 50),
                )

                for x, y, width, height in faces:
                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + width, y + height),
                        (0, 255, 0),
                        2,
                    )

                cv2.imshow('Camera', frame)

                if len(faces) > 0:
                    # Find next available filename
                    while os.path.exists(image_constant):
                        image_number += 1
                        image_constant = file_name + '_' + str(image_number) + '.png'
                    
                    cv2.imwrite(image_constant, frame)
                    print(f'Face detected. Image saved as {image_constant}.')
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            print('Releasing camera and closing windows.')
            cam.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    Camera().capture_when_face_detected()
