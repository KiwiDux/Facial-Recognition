import cv2, os, sys, time

detector_model = 'face_detection_yunet_2023mar.onnx'
recognizer_model = 'face_recognition_sface_2021dec.onnx'
employee_folder = 'employees'
match_threshold = 0.363

class Camera:   # Captures face crops from the webcam and stores them per person.

    
    def __init__(self, folder = 'employees', padding = 40, min_sharpness = 0.15):
        self.folder = folder                # folder to save images
        self.padding = padding              # fraction of face size added around the box
        self.min_sharpness = min_sharpness  # reject blurry frames (Laplacian)
        
        xml = 'haarcascade_frontalface_default.xml'
        self.face_detector = cv2.CascadeClassifier(xml)
        if self.face_detector.empty():
            raise RuntimeError(f'Unable to load the face detector xml file: {xml}.')
 
 
    def detection_setting(self, scale_factor = 1.0, min_neighbors = 3, min_size = (70, 70)):
        self.scale_factor = scale_factor    # lower = stricter (dlib default is 0.6)
        self.min_neighbors = min_neighbors  # how many neighbors each candidate rectangle should have to retain it
        self.min_size = min_size            # minimum possible object size. Objects smaller than that are ignored. e.g. (70, 70) pixels
        
        gray_captured = cv2.cvtColor(cv2.imread('test_image.jpg'), cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray_captured,
            scaleFactor = self.scale_factor,
            minNeighbors = self.min_neighbors,
            minSize = self.min_size,
        )
        return faces
 
    
    def crop_face(self, image, x, y, width, height):
        added_space = self.padding
        x_start = max(0, x - added_space)
        y_start = max(0, y - added_space)
        x_end = min(image.shape[1], x + width + added_space)
        y_end = min(image.shape[0], y + height + added_space)
        return image[y_start:y_end, x_start:x_end]
 
 
    def capture_face(self, faces, input_name):
        cam = cv2.VideoCapture(0)   # 0 = default 
        if not cam.isOpened():
            print('Failed to open camera.')
            return []
 
        os.makedirs(self.folder, exist_ok = True)   # Create folder if it doesn't exist
        file_name = f'captured_image_{input_name}'
        count = 5                   # number of images to capture
        last_save_time = 0          # Track when last image was saved
        saved_images = []           # (file name, time taken) of every image saved this session
 
        image_number = 1            # first free image number, so existing images are not overwritten
        while os.path.exists(os.path.join(self.folder, f'{file_name}_{image_number}.png')):
            image_number += 1
 
        try:
            while len(saved_images) < count:
                ret, frame = cam.read()
                if not ret:
                    print('Failed to capture image.')
                    break
 
                # save image if exactly one face is detected and 5 seconds have passed since last save
                if len(faces) == 1 and time.time() - last_save_time >= 5:
                    x, y, width, height = faces[0]
                    cropped_face = self.crop_face(frame, x, y, width, height)   # crop before drawing the box
                    grayscale_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2GRAY)
 
                    image_file = os.path.join(self.folder, f'{file_name}_{image_number}.png')
                    cv2.imwrite(image_file, grayscale_face)
                    last_save_time = time.time()
                    saved_images.append((os.path.basename(image_file), last_save_time))
                    image_number += 1
                    print(f'Face detected. Image saved as {image_file}.')
 
                for x, y, width, height in faces:
                    cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 1)
 
                cv2.imshow('Camera', frame)
 
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            print('Stopping camera and closing window.')
            cam.release()
            cv2.destroyAllWindows()
 
        return saved_images
