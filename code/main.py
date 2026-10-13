from rich.console import Console
from nfc_reader import read_card_id
from employee import identify_employee, employee_folder, load_info, add_pictures
from camera import Camera
console = Console()

if __name__ == '__main__':
    def main_menu():
        try:
            while True:
                console.print('\n[bold cyan]=== Control Panel ===[/bold cyan]')
                console.print('1. Employee Login')
                console.print('2. Employee Management')
                console.print('3. Admin Panel')
                console.print('4. Exit')

                choice = console.input('Select option: ').strip()

                if choice == '1':
                    return
                    
                elif choice == '2':
                    return
                    
                elif choice == '3':
                    return

                elif choice == '4':
                    console.print('[cyan]Exiting control panel.[/cyan]')
                    break

                else:
                    console.print('[red]Invalid choice.[/red]')
        
        finally:
            console.print('[cyan]Control panel closed.[/cyan]')

    #uid = read_card_id()
    uid = input('Enter the card UID (or scan a card): ')
    uid, input_name = identify_employee(uid)
    camera = Camera(folder = employee_folder(uid))

    if load_info(uid)['pictures']:      # known person: check the face against the saved pictures
        if camera.verify_face():
            print(f'Welcome {input_name}.')
        else:
            print('Face does not match this card.')
    else:                               # no pictures yet: capture them
        saved_images = camera.capture_face(input_name)
        add_pictures(uid, saved_images)