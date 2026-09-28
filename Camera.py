import cv2, os, sys, time, csv

user_id = input('Enter your user ID: ') # Need to change get ID from NFC reader

class Camera:
    def capture_detected_face(self):
        cam = cv2.VideoCapture(0)   # 0 = default 
        xml = 'haarcascade_frontalface_default.xml'
        face_detector = cv2.CascadeClassifier(xml)
        
        file_name = 'captured_image' + time.strftime('%Y%m%d-%H%M%S')  # File name based on timestamp
        folder_name = user_id + '_Photo'  # Folder name based on user ID
        # Create folder
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        image_number = 1
        image_file = os.path.join(folder_name, file_name + '_' + str(image_number) + '.png')
        user_image = cv2.imread(file_name)
        last_save_time = 0  # Track when last image was saved
        
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
                    minNeighbors = 1,   # Used when comparing reference image with captured image 'Neighbors' is the number of faces detected.
                    minSize = (50, 50),
                )
    
                for x, y, width, height in faces:
                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + width, y + height),
                        (0, 255, 0),
                        1,
                    )
                    
                    # Add extra space around the detected face
                    added_space = 40
                    x_start = max(0, x - added_space)
                    y_start = max(0, y - added_space)
                    x_end = min(frame.shape[1], x + width + added_space)
                    y_end = min(frame.shape[0], y + height + added_space)
                    cropped_face = frame[y_start:y_end, x_start:x_end]

                cv2.imshow('Camera', frame)

                if len(faces) == 1:  # Only save image if exactly one face is detected
                    current_time = time.time()
                    # Only save image if 5 seconds have passed since last save
                    if current_time - last_save_time >= 5:
                        # Find next available file name
                        while os.path.exists(image_file):
                            image_number += 1
                            image_file = os.path.join(folder_name, file_name + '_' + str(image_number) + '.png')

                        grayscale_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
                        cv2.imwrite(image_file, grayscale_face)
                        print(f'Face detected. Image saved as {image_file}.')
                        last_save_time = current_time

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            print('Releasing camera and closing windows.')
            cam.release()
            cv2.destroyAllWindows()


if __name__ == '__main__':
    Camera().capture_detected_face()
