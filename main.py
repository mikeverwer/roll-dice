#!/usr/bin/env python
import PySimpleGUI as sg
import random
import numpy as np
import webbrowser
# required files
import classes as cl
import make_window as make


# Close the splash screen.
try:
    import pyi_splash
    pyi_splash.close()
except:
    pass



images = image_data()

# ----------------------------------------------------------------------------------------------------------------------

def error_popup(error, message, duration=5):
    sg.popup_quick_message(f'\n{error}\n\n{message}\n', background_color='#1b1b1b', text_color='#fafafa', auto_close_duration=duration, grab_anywhere=True, keep_on_top=False)

# -------------------------------------------------------------------------------------------------------------------------
#   Beginning of GUI Code
# -------------------------------------------------------------------------------------------------------------------------
def main():
    # ---------------------------------------------------------------------------------------------------------------------
    # Initialize Window
    # ---------------------------------------------------------------------------------------------------------------------
    sg.theme('Default1')
    # Build the Mainframe, see classes.py -> Mainframe
    mf = cl.Mainframe(images) 
    mf.window = make.Mainframe_func(sg, images, theme='Default1', frame=mf) 
    # size = mf.window.size


    # logging = False
    # full_logging = False

    # ----------------------------------------------------------------------------------------------------------------------
    # Event Loop
    # ----------------------------------------------------------------------------------------------------------------------

    while True:
        event, mf.values = mf.window.read(timeout = 1000 // mf.update_interval)
        run_again = mf.maestro.handle(event)
        if not run_again:
            break

    # end of event loop
    mf.window.close()


if __name__ == '__main__':
    main()
