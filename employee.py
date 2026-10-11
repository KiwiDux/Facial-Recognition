import json, os, time


employee_folder = 'employees'


def timestamp(t=None):      #Format a time (seconds since epoch, default now) as 'YYYY-MM-DD HH:MM:SS'
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))


def employee_folder(uid):
    return os.path.join(employee_folder, uid)


def save_info(uid, info):
    os.makedirs(employee_folder(uid), exist_ok=True)
    with open(os.path.join(employee_folder(uid), 'info.json'), 'w') as f:
        json.dump(info, f, indent=2)


def load_info(uid):
    with open(os.path.join(employee_folder(uid), 'info.json')) as f:
        return json.load(f)


def identify_employee(uid):     #Return (uid, name) for a card UID and record the login time. Unknown cards are registered first
    try:
        info = load_info(uid)
    except FileNotFoundError:  # card not registered yet
        name = input('New card. Enter the name of the person: ')
        info = {'name': name, 'pictures': {}}

    info['last_logged'] = timestamp()
    save_info(uid, info)
    return uid, info['name']


def add_pictures(uid, saved_images):        #Record when each picture was taken. saved_images is a list of (file name, time taken)
    info = load_info(uid)
    for file_name, taken in saved_images:
        info['pictures'][file_name] = timestamp(taken)
    save_info(uid, info)