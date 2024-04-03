import PySimpleGUI as sg

def ImageButton(image_path):
    """
    A User Defined Element. It looks like a Button, but is an Image element
    :param image_path: The path to the image file
    :return: A Image element with a tuple as the key
    """
    return sg.Image(image_path, key=('-B-', image_path), enable_events=True, background_color='white')

def do_binds(window, button_images):
    """
    This is magic code that enables the mouseover highlighting to work.
    """
    for image_path in button_images:
        window[('-B-', image_path)].bind('<Enter>', 'ENTER')
        window[('-B-', image_path)].bind('<Leave>', 'EXIT')

def main():
    # Define the paths to the button images
    button_images = ['assets/die1.png', 'assets/die2.png', 'assets/die3.png']
    hover_images = ['assets/lock1.png', 'assets/lock2.png', 'assets/lock3.png']

    # The window's layout
    layout = [[ImageButton(image_path) for image_path in button_images],
              [sg.Text(font='_ 14', k='-STATUS-')],
              [sg.Button('Ok'), sg.Exit()]]

    window = sg.Window('Custom Mouseover Highlighting Buttons', layout, finalize=True)

    # After the window is finalized, then we can perform the bindings
    do_binds(window, button_images)

    # The Event Loop
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        # if the event is a tuple, it's one of our ImageButtons
        if isinstance(event, tuple):
            # if the second item is one of the bound strings, then do the mouseover code
            if event[1] in ('ENTER', 'EXIT'):
                image_path = event[0]
                if event[1] == 'ENTER':
                    window[image_path].update(source=button_images[1])
                if event[1] == 'EXIT':
                    window[image_path].update(hover_images[1])
            else:  # a "normal" button click (Image clicked), so print the path of the image
                window['-STATUS-'].update(f'Button pressed = {event[0]}')
    window.close()

if __name__ == '__main__':
    main()
