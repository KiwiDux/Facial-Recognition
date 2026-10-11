from nfc_reader import read_card_id
from employee import identify_employee, employee_folder, add_pictures
from camera import Camera


if __name__ == '__main__':
    uid = read_card_id()
    uid, input_name = identify_employee(uid)
    camera = Camera(folder = employee_folder(uid))
    faces = camera.detection_setting()
    saved_images = camera.capture_face(faces, input_name)
    add_pictures(uid, saved_images)