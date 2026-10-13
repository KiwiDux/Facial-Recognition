import cv2, os, time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Facial-Recognition/
datasets = os.path.join(base_dir, 'datasets')
detector_model = os.path.join(datasets, 'face_detection_yunet_2026may.onnx')
recognizer_model = os.path.join(datasets, 'face_recognition_sface_2021dec.onnx')

match_threshold = 0.363 # cosine similarity needed for a match | default = 0.363 (higher = stricter)


class Camera:   # Captures face images from the webcam, stores them per person and checks faces against them.


    def __init__(self, folder = 'employees', min_sharpness = 50, score_threshold = 0.8):
        self.folder = folder                    # folder to save images
        self.min_sharpness = min_sharpness      # reject blurry faces (Laplacian variance)

        for model in (detector_model, recognizer_model):
            if not os.path.exists(model):
                raise RuntimeError(f'Unable to find the model file: {model}.')

        self.detector = cv2.FaceDetectorYN.create(detector_model, '', (320, 320), score_threshold)  # input size is set per frame
        self.recognizer = cv2.FaceRecognizerSF.create(recognizer_model, '')


    def frames(self):   # Yields webcam frames and releases the camera when the loop ends
        cam = cv2.VideoCapture(0)   # 0 = default
        if not cam.isOpened():
            print('Failed to open camera.')
            return

        try:
            while True:
                ret, frame = cam.read()
                if not ret:
                    print('Failed to capture image.')
                    break
                yield frame
        finally:
            print('Stopping camera and closing window.')
            cam.release()
            cv2.destroyAllWindows()


    def detect_faces(self, frame):
        self.detector.setInputSize((frame.shape[1], frame.shape[0]))
        faces = self.detector.detect(frame)[1]
        return [] if faces is None else faces   # each face: x, y, width, height, 5 landmarks, score


    def show(self, frame, faces):   # Draw a box around every face, show the frame, return True when 'q' is pressed
        for face in faces:
            x, y, width, height = face[:4].astype(int)
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 1)
        cv2.imshow('Camera', frame)
        return cv2.waitKey(1) & 0xFF == ord('q')


    def sharpness(self, image):
        return cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()


    def capture_face(self, input_name):
        os.makedirs(self.folder, exist_ok = True)   # Create folder if it doesn't exist
        file_name = f'captured_image_{input_name}'
        count = 5                   # number of images to capture
        last_save_time = 0          # Track when last image was saved
        saved_images = []           # (file name, time taken) of every image saved this session

        image_number = 1            # first free image number, so existing images are not overwritten
        while os.path.exists(os.path.join(self.folder, f'{file_name}_{image_number}.png')):
            image_number += 1

        for frame in self.frames():
            faces = self.detect_faces(frame)

            # save image if exactly one face is detected and 5 seconds have passed since last save
            if len(faces) == 1 and time.time() - last_save_time >= 5:
                aligned_face = self.recognizer.alignCrop(frame, faces[0])   # 112x112 face, straightened using the landmarks
                if self.sharpness(aligned_face) >= self.min_sharpness:
                    image_name = f'{file_name}_{image_number}.png'
                    cv2.imwrite(os.path.join(self.folder, image_name), aligned_face)
                    last_save_time = time.time()
                    saved_images.append((image_name, last_save_time))
                    image_number += 1
                    print(f'Face detected. Image saved as {image_name}.')
                    if len(saved_images) == count:
                        break

            if self.show(frame, faces):
                break

        return saved_images


    def load_features(self):    # Feature vector of every saved picture of this person
        features = []
        for file in os.listdir(self.folder):
            if file.endswith('.png'):
                features.append(self.recognizer.feature(cv2.imread(os.path.join(self.folder, file))))
        return features


    def verify_face(self):      # When there is a face in front of the camera matches a saved picture
        saved_features = self.load_features()
        if not saved_features:
            print('No saved pictures for this person.')
            return False

        for frame in self.frames():
            faces = self.detect_faces(frame)

            if len(faces) == 1:
                feature = self.recognizer.feature(self.recognizer.alignCrop(frame, faces[0]))
                for saved in saved_features:
                    if self.recognizer.match(feature, saved, cv2.FaceRecognizerSF_FR_COSINE) >= match_threshold:
                        return True

            if self.show(frame, faces):
                break

        return False