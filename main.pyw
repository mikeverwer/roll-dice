#!/usr/bin/env python
# .requirements
import random
from typing import Self
import numpy as np
import webbrowser
# required files
import PySimpleGUI as sg
import classes as cl
import make_window as make

# Close the splash screen. Only runs if the program runs from an executable.
try:
    import pyi_splash # type: ignore - ignore compiler warning
    pyi_splash.close()
except:
    pass

# -------------------------------------------------------------------------------------------------------------------------
#   Beginning of GUI Code
# -------------------------------------------------------------------------------------------------------------------------
def main():
    """
    Builds the Mainframe (see classes.py -> Mainframe) and houses the event loop.
    
    make_Mainframe() makes the window that the frame uses.  It creates the layout for the window and calls sg.Window(...).
    After the window is made, it instantiates the graphs and creates the Convolution and the EventHandler.  
    Finally, it then returns the sg.Window.

    The Window is read in the event loop, then the EventHandler, maestro, uses the handle(event) method to decide how
    the frame will react. 
    """
    mf = cl.Mainframe() 
    mf.window = make.make_Mainframe(sg, theme='Default1', frame=mf)

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
