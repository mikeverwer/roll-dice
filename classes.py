import random
from typing import Self
import PySimpleGUI as sg
import numpy as np
import webbrowser

"""
The classes required for the Roll Dice simulation window.  The utilization of the classes is described below.

A `Mainframe` houses the sg.Window object and the values dictionary, the convolution of the `n` die, as well as 
the simulation of the rolls.  It also has an `EventHandler` to handle the events from window.read().

A `Convolution` is an object that has a convoluted distribution graph with each of the bars of the graph being
their own individual `Bar` objects.  This is the theoretical probability distribution for rolling the `n` dice.

The `Simulation` class controls the entire simulation. It is invoked as an object by the `EventHandler` and the step is 
incremented there.  The simulation creates `Roll` objects and draws them on the graph.  
Each `Roll` is remembered by the `simulation` and, when selected, will display the outcome of each die rolled.

Note: A `Simulation` requires a `Mainframe` and information about the `Convolution` to be instantiated, so it 
    can only be created AFTER the Mainframe has been fully instantiated. Whereas the `mainframe` instantiates 
    its own `convolution`.  

The figure below is a usage network, NOT a class structure tree.

           _____Frame_____ 
          /       |       \
         /  Event Handler  \
        /                   \
   Convolution    /----> Simulation
        |        /      /          \ <--- *not a true connection, only accesses the sim graph
       Bar -----/     Roll ----> DieFace

"""

# ----------------------------------------------------------------------------------------------------------------------
# 8888888888                           888         888    888                        888 888                  
# 888                                  888         888    888                        888 888                  
# 888                                  888         888    888                        888 888                  
# 8888888   888  888  .d88b.  88888b.  888888      8888888888  8888b.  88888b.   .d88888 888  .d88b.  888d888 
# 888       888  888 d8P  Y8b 888 "88b 888         888    888     "88b 888 "88b d88" 888 888 d8P  Y8b 888P"   
# 888       Y88  88P 88888888 888  888 888         888    888 .d888888 888  888 888  888 888 88888888 888     
# 888        Y8bd8P  Y8b.     888  888 Y88b.       888    888 888  888 888  888 Y88b 888 888 Y8b.     888     
# 8888888888  Y88P    "Y8888  888  888  "Y888      888    888 "Y888888 888  888  "Y88888 888  "Y8888  888   
#   
# - A class that handles the events from the event loop in main
# ----------------------------------------------------------------------------------------------------------------------
class EventHandler:
    def __init__(self, frame) -> None:
        self.mf: Mainframe = frame
        self.logging = False
        self.full_logging = False


    def error_popup(self, error, message, duration=5) -> None:
        sg.popup_quick_message(f'\n{error}\n\n{message}\n', background_color='#1b1b1b', text_color='#fafafa', auto_close_duration=duration, grab_anywhere=True, keep_on_top=False)


    def handle(self, event) -> bool:
        """
        Handles the event from Window.read()
        Returns: - False if the window has been closed, triggers the end of the event loop in main.py.
                 - True otherwise.
        List of events - Read as follows: event key - description of outcome
            exit, sg.WINDOW_CLOSED
            (hover, key) for key in hover_images - change the buttons image data to the hover/non-hover version or click the button
            resize, <Configure> - resize the window
            Clear - clears log
            face[number] - slider representing die face [number] has been moved, activate all sliders
            lock[number] - lock/unlock the slider for die face [number] and change the icon of the button
            preset - set the slider to one of preset distributions
            add preset - add the current slider configuration to the list of preset distributions
            Randomize - generate a random distribution for a d6 and set the sliders to it
            up, down, dice - change the number of dice to throw
            go - start the simulation
            Pause - pause/play the simulation
            convolution graph - clicked the convolution graph, activate hit detection/outcome
            simulation graph - clicked the simulation graph, activate hit detection/outcome
        """
        mf = self.mf
        size = None

        # the code from inside the event loop goes here.
        mf.sim_graph = mf.window['simulation graph']
        mf.con_graph = mf.window['convolution graph']

        # log events and handle closing
        if event not in (sg.TIMEOUT_EVENT, sg.WIN_CLOSED):
            if self.logging:
                print(f'============ Event :: {event} : {mf.values[event] if event in mf.values else None} ==============')
                if (self.full_logging == True or event == 'show values'):
                    print('-------- Values Dictionary (key=value) --------')
                    for key in mf.values:
                        print(f'\'{key}\' : {mf.values[key]},')
        if event in (None, 'exit', sg.WINDOW_CLOSED):
            print("[LOG] Clicked Exit!")
            mf.window.close()
            return False

        # if the event is a tuple, it's a hover-button
        if isinstance(event, tuple):
            # if the second item is one of the bound strings, then do the mouseover code
            if event[1] in ('ENTER', 'EXIT'):
                key = event[0]
                image_tag = event[0][1]
                if event[1] == 'ENTER':
                    image_b64_data = getattr(mf.images, image_tag + '_hover')
                    mf.window[key].update(data=image_b64_data)
                if event[1] == 'EXIT':
                    image_b64_data = getattr(mf.images, image_tag)
                    mf.window[key].update(data=image_b64_data)
            else:  # Image clicked
                button_clicked = event[1]
                if button_clicked == 'exit':
                    print("[LOG] Clicked Exit!")
                    mf.window.close()
                    return False
                elif button_clicked == 'menubar_CLT':
                    webbrowser.open('https://mikeverwer.github.io/articles/the-clt.html')
                elif button_clicked == 'author':
                    webbrowser.open('https://mikeverwer.github.io/')
                elif button_clicked == 'minimize':
                    pass

        elif event == 'resize':
            if size != mf.window.size:
                mf.resize_graphs()
                size = mf.window.size

        elif event == 'SaveSettings':
            filename = sg.popup_get_file('Save Settings', save_as=True, no_window=True)
            mf.window.SaveToDisk(filename)
            # save(values)
        elif event == 'LoadSettings':
            filename = sg.popup_get_file('Load Settings', no_window=True)
            mf.window.LoadFromDisk(filename)
            # load(form)

        elif event == 'Clear':
            mf.window['log'].update(value='')

        elif event.startswith('face'):
            mf.activate_slider(event=event)
            mf.window['rolls'].set_focus()

        elif event.startswith('lock'):
            active_lock = int(event[-1])
            mf.activate_lock(active_lock)

        elif event == 'preset':
            set_to_preset = mf.values[event]
            mf.set_sliders_to(mf.presets[set_to_preset], reset_locks=True)

        elif event == 'add preset' and mf.values['preset'] != '':
            mf.add_preset(mf.values['preset'])

        elif event == 'Randomize':
            if False in mf.locks:  # At least 1 slider is unlocked
                mf.die_distribution = mf.random_distribution(get_var=True)
                mf.window['preset'].update(value='')
                mf.window['Randomize'].set_focus()

                mf.set_sliders_to(mf.die_distribution)

            mf.die_distribution = [mf.values[f'face{i}'] for i in range(1, 7)]
            mf.mean_and_deviation(update=True)

        elif event == 'up' or event == 'down' or event == 'dice':
            if event != 'dice':
                delta = 1 if event == 'up' else -1
                mf.dice_change(mf.dice + delta)
            else:
                try:
                    mf.dice_change(value=mf.values[event])
                except ValueError as ve:
                    self.error_popup(error='Value Error', message=ve)

        elif event == 'go':  # Run the show
            # Get the number of dice to roll and rolls to perform
            try:
                if int(mf.values['dice']):
                    # Run the simulation
                    mf.simulate = True
                    mf.sim = Simulation(mf)
            except ValueError as ve:
                mf.simulate = False
                self.error_popup(error='Value Error', message=ve)
        
        elif event == 'Pause' and mf.sim:
            mf.simulate = not mf.simulate
            new_text = 'Pause' if mf.simulate else "Play"
            mf.window['Pause'].update(text=new_text)

        elif event == 'convolution graph':
            try:
                hit_bin: Bar = None
                mf.convolution.selection_box_id, hit_bin = mf.activate_hit_detect(
                    click=mf.values[event], graph=mf.con_graph, event=event,
                    objects=mf.convolution.bins, prev_selection=(mf.convolution.selection_box_id, None),
                    offset=(0, 15)
                )
            except TypeError:
                mf.convolution.selection_box_id = None
        
        elif event == 'simulation graph' and mf.sim:
            try:
                hit_roll: Roll = None
                mf.sim.selection_box_id, hit_roll = mf.activate_hit_detect(
                    click=mf.values[event], graph=mf.sim_graph, event=event, 
                    objects=mf.sim.rolls, prev_selection=(mf.sim.selection_box_id, None)
                )
                mf.sim.displaying_roll = True
            except TypeError:
                mf.sim.selection_box_id = None
                mf.sim.displaying_roll = False
                mf.sim.delete_ids()

        
        ######################################
        # Animation
        ######################################
        if mf.simulate:
            if mf.sim.trial_number <= mf.sim.number_of_rolls:
                mf.sim.roll_dice(mf.sim.trial_number)
                mf.sim.trial_number += 1
            else:
                mf.simulate = False
                max_bin = None
                max_length = 0
                for bin, outcomes in mf.sim.bin_dictionary.items():
                    if len(outcomes) > max_length:
                        max_bin = bin
                        max_length = len(outcomes)
                self.error_popup(error='Finished!', message=f'The sum with the most outcomes was {max_bin},\nwhich was rolled {max_length} times.', duration=4)

        return True  # tells the event loop to run again


# ----------------------------------------------------------------------------------------------------------------------
# 888b     d888          d8b           .d888                                        
# 8888b   d8888          Y8P          d88P"                                         
# 88888b.d88888                       888                                           
# 888Y88888P888  8888b.  888 88888b.  888888 888d888 8888b.  88888b.d88b.   .d88b.  
# 888 Y888P 888     "88b 888 888 "88b 888    888P"      "88b 888 "888 "88b d8P  Y8b 
# 888  Y8P  888 .d888888 888 888  888 888    888    .d888888 888  888  888 88888888 
# 888   "   888 888  888 888 888  888 888    888    888  888 888  888  888 Y8b.     
# 888       888 "Y888888 888 888  888 888    888    "Y888888 888  888  888  "Y8888  
#
# - An object that has the sg.Window and the values from window.read() as well as all of the required
#             variables for the simulation and convolution graphs. Events are explicitly handled in main, but 
#             most events have mainframe class methods that handle all actions.
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# Image Data
# ----------------------------------------------------------------------------------------------------------------------
class ImageData:
    def __init__(self):
        """
        The base64 data for the images used by the frame.
        """
        self.die1 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAF+SURBVEiJ5ZWxTgIxHMY/Lxa5jXYhLPSGm9W43wOQ3jEdD8BkiJPxNYwPwQwMkBv1FUx8AjmTa12OY6ECSesiDi42gomJv7X//Pq1+ZL/ET4ghFxwzm8ppW3f9088z4MrxhhordeLxSKfz+c32+328fOQc37V7XZflVJ2H6SUNo5jFQTB4DNxkiTKGLOXeIcxxsZxrAgh5wjD8GHfxF8pisKGYXjvUUp5s9l0/l8XWq0WGo0G9+r1eu2g5g983z9xr8QP+Afy2WyGfr+PLMvc7VEUvXxXrel0ahljFoBljNksy76tYxRFL07JJ5MJyrIEAJRlidFo5BTcSZ6mKRhjAADGGHq9npP82GVICIHhcIjxeIw0TdHpdA4n310ghHAdB/BXqvj35Frr9W+ItdZrr6qquVLqoGIpJZbL5TMIIeeH3kRCCFWr1U4BAEEQDJIkUVLKvcRFUVghhGq325cAcLR7CiHkjHN+RynlP9n+q9XqraqqPM/z681m8wQA774nKEMISi18AAAAAElFTkSuQmCC'
        self.die2 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAG9SURBVEiJ7VW9btpQGD2xdAkejTcPXA9mTaMKxotkVttsvAJV1KnKA4DEAEPVF2AHBh6hqYSQ50pdKQNGsp0BwcQtf74dErukWZCdMWc9V+f7ud93vis8gxDykVL6VVGUoizL15Ik4VJEUQTO+W69XnuLxeL+cDj8TEhK6ed6vf4YhqHIgiAIhG3boa7rd0nGjuOEURRlEo4RRZGwbTskhNzCMIwf5xnPZjPR7XaF67qpA/i+LwzDeEClUpmfC2uaJgAIVVXFYDBIHaBcLv+W8vl8Lu79eDyG7/sAgNVqhX6/f/Gn/g9Zlq9fjES1WoWqqjGJWq2WWhwAwBhbnpczHA6FaZqi0+mI4/GYui2MseUr8bcCY2x5+aakwLv4u/g/nE4ntNttmKaJ0Wj0+kGWOW+1WkKW5cSLzs0u85xPJhNwzgE8edF0On3BS5zzXVrxZrOJQqEAANA0DY1GI+E45zsYhvEQBEHqNXddV/R6PTGfJ84tfN8XpVLpOwght299iSzLCnO53A0AQNf1O8dxwiwVxBlblhUWi8VPAHAV94gQ8oFS+k1RFJrm+m+32z+bzcbzPO/Lfr//BQB/ATmrZWX1MPnyAAAAAElFTkSuQmCC'
        self.die3 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIaSURBVEiJrVU9j9pAFJxDWQ6XXjoX2IVpk1MEpZFMh2yozA+gITqlivIDQKKAIsofoKMACqAA0eUiIUR9UlpCAUjGKfiocODAmyIBQe4iOYZp39O82dnZtzf4A0LIW1EUP/E8H+I47tbn88EtHMeBbdub5XI5GY/HH5+enh6PRVEU36dSqR+WZbFLMJvNmK7rliRJ90fFyWTSchznIuIDHMdhuq5bhJA7yLL89VTxcDhkxWKRDQYDzwNM02SyLD8gGo2OTokFQWAAWDAYZNVq1fOASCTy3RcIBPwH7xuNBkzTBADM53OUy2XXl/o3OI67PYtELBZDMBg8FBGPxz2TAwAURZmeHqdWqzFVVVmhUGC73c6zLYqiTJ+RXwuKokxdv5ROp4NMJoNut+vdlpfQbrcZpZQBYJRS1u12r6e81WphsVgAABaLBRqNhivhrsgNwwClFABAKUU6nXZF/spNk6ZpqFQqaDabMAwDiUTieuSHAZqmuW0H4NKWf2G/3yOfz0NVVdTr9ecNl+Q8l8sxjuOOu+h02f1Xzl9Cr9eDbdsAfu+ifr9/VvfZtr3xSp7NZo8pEgThLEW2bW8gy/LDbDbz6gwbDAasVCqx0ei4uZlpmiwcDn8BIeTu2j+RpmmW3+9/DQCQJOk+mUxal5zgoFjTNCsUCr0DgJuDR4SQN6IofuZ5XvTy+6/X65+r1WoymUw+bLfbbwDwCxlCy8JiS1i/AAAAAElFTkSuQmCC'
        self.die4 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIzSURBVEiJ7VW7jtpQED2LZHZNB+4osAvTJqvIlEYyLY/fiFaponwAyBS4iPIDUPIq+IRsEMKIMtK2mAKQLk7BozIJD0+KBAsvkoXYraKccmbuuTNzZ869wV9wHPdOFMXP0Wg0wfP8bSgUwqVwXRebzebXarWaTiaTT7vd7rvnFEXxQ6FQ+GHbNr0E8/mccrmcLUnSg5dxPp+3Xdd9EfERrutSLpezOY67hyzL304zHo1GVKlUaDAYXERmmiZVKhWyLMuzMcZIluVHpFKp8SlxPB4nACQIAjWbzUDier1OsViMAFA8HvddoCiKFbq7uwsfe9/pdMAYAwAsFgtUq9XAh6zValgulwAAxhg6nY7n43n+1jcS6XQagiAcnchkMoHkmUwGkUgEACAIAtLptD9AVdXZaamtVos0TaNyuUz7/T6wLfv9nnRdJ03TqN1u+3yqqs7OyF8LqqrOLt+UK/Cf/F8nbzQa0DQNuq7jcDgEHj4cDiiVStA0De12+zzgdM5N0/S0IhKJkK7rgbNcLBaJ53lPi07F7mzOTdP0tMJxHHS73cDMe70eNpsNgD9a1O/3/QGKonhSZlmWTxWfr/RzNJtNnyqOx57AkqIoFmRZfpzP557RsiwyDIOGw+FFaz4YDMgwDB8xY4ySyeRXcBx3/9o/UTabtcPh8BsAgCRJD/l83j6t4BowxiibzdqJROI9ANwce89x3FtRFL9Eo1Hxmt/fcZyf6/V6Op1OP2632ycA+A36gJvsW+G55QAAAABJRU5ErkJggg=='
        self.die5 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAKSSURBVEiJrVU9b9pQFD1BNcFs2BsDZnDWNqqc0UhmiwxM5AdkqqJOVX9AImeAoeofSKaIrwEyJGJLihBGGSt1jTOESA93CDBBm4BvhxYLh8i1Es747n3n3Xffueet4R84jnsvSdKXWCyW4Hl+PRQKISgcx8FkMvk9HA57t7e3nx8fH7+7QUmSPuZyuZ+2bdNr0O/3KZPJ2Mlkcs+tOJvN2o7jvIp4DsdxKJPJ2BzHbUKW5W+LFV9fX1OhUKButxuIzDRNKhQKZFmWu8YYI1mWL7G1tXWzSByPxwkAiaJIlUrFl7hUKpEgCASA4vG45wBFUaxQJBIJz3tfr9fBGAMA3N/f4+joyPchj4+PMRgMAACMMdTrdTfG8/y6RxKpVAqiKM6DSKfTvuTpdBrRaBQAIIoiUqmUN0FV1bvFq1arVdI0jQ4PD2k6nfq2ZTqdkmEYpGka1Wo1T0xV1bsl8lVBVdW7wJNyfn6O3d1dNJvNoFuW2/Iczs7OXFUIgkDNZnN1lZ+enrqqGAwGHlX4IRB5Pp+HIAgAAEEQsLOzE4j8TZAkXddxcnKCRqOBfD6P7e3t1ZHPD9B1PWg6gGfaUi6XoWkaDMPAbDbz3TybzXBwcABN01Cr1ZYTFtVimqarimg0SoZh+Cpif3+feJ53vWjR7JbUYpqmq4rxeIxWq+VbebvdxmQyAfDXizqdjjdBURTXyizL8rji05F+ikql4nHFmxvXYElRFAuyLF/2+3130bIsKhaLdHV19d9BISLqdrtULBY9xIwx2tjYuADHcZur/ol0XbfD4fBbAEAymdzLZrP24g1eAsYY6bpuJxKJDwCwNu89x3HvJEn6GovFpJf8/uPx+NdoNOr1er1PDw8PPwDgD9oXAlg17L5iAAAAAElFTkSuQmCC'
        self.die6 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALOSURBVEiJvVU9T9tQFD1EcsAZjIIlI2XAGczaosqMjuSMxGGAX2CWCnWq+gNAZkiGqhJihDEOGSLYYClFgC3GQlfMQJAcg8SHMiQtJL4daKyYCBdB1TO+e3Xeeee9e94A/oBhmHeiKH5OJpNjLMsOxmIxPBe+76PVav26ubmpnZ2dfbq/v/8eFEVR/DA9PX3heR69BvV6nTRN89Lp9HygOJ/Pe77vv4q4C9/3SdM0j2GYCUiS9K1X8cnJCRUKBbJt+1lklmVRoVAgx3GCNdd1SZKkHUxOTp72EqdSKQJAPM9TuVyOJC6VSjQyMkIAKJVKhTaQZdmJDQ0NxbveV6tVuK4LALi6usLq6mrkRa6treH6+hoA4LouqtVqUGNZdjD0JDKZDHie7xaRzWYjybPZLBKJBACA53lkMplwg6Io571HXV9fJ1VVaWlpidrtdqQt7XabDMMgVVWpUqmEaoqinPeR/ysoinLeNyn7+/vQdR2maUZa0kWpVMLc3Bxs2+4v9io/OjoiQRAIAHEcRysrK5HqlpeXieM4AkCjo6N0fHz8tPLt7W1cXl4CABqNBjY2NiJVb25uotFoAAAuLi6wtbUVqofIp6amIAgCAGB4eBizs7OR5DMzM+A4DgAgCAI0TXvaFqKHidN1/a8D1IVpmqTret9E///XYpomVFWFYRjodDqRtnQ6HSwuLkJVVVQqlf6GXuWWZQVZkUgkyDCMSHULCwvEsmyQRb3W9Cm3LCvIimazid3d3Ujle3t7aLVaAB6y6ODgINwgy3IQZY7jhFLx8Ug/RrlcDqXi6WkQsCTLsgNJknbq9Xqw6DgOFYtFOjw8fNbF2bZNxWIxROy6Lo2Pj38FwzAT//onyuVyXjwefwMASKfT8/l83us9wUvgui7lcjlvbGzsPQAMdL1nGOatKIpfksmk+JLfv9ls/ry9va3VarWPd3d3PwDgN0sYp3npWVpUAAAAAElFTkSuQmCC'
        self.down = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAKCAYAAABfYsXlAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD6SURBVCiRtZLBSkJBFIa/40x3sH0ubGuQ1VtEbao3iFpGCdZbRCBEb2D5BhVCl3yM3Nrqgrdtone4dFpIodaNm+C3m5l/vjM/jISdtrIgCsCi5GonV0ni6b500TnmCcLm1gZBEHzvTcmdGx9cN27o92OcCzDGkoX3njRNqaxVqJ/XpsQAEnbaH4DMNrhrtni4fyRJPKo/mzjnsEuW07MTdna3EZHZiP4q/6LXe+XqskEURYyGIwCMMVhr2D/Y4+j4kOJyMavY33IAVSV8eua22WLwPqBaXad+UaO8Ws66kl8+SRy/USqt5IkCaCFvEviPGBj/81yvngP5BK0MVHD9uAUFAAAAAElFTkSuQmCC'
        self.lock1 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAGySURBVEiJ5dVPSxtBGMfx38xmsp0lRhOKRQ8NaGv2kFUQX0QvPYhVtFLsvafq3dJ76bVXD4qrMeLJV6EWmoSsovjnoC60aHbb3WzGzfSiPZQWts0Kgt/zw2eGYeAhuM5kbDjoTH8IOX8sGVMlIYgakRJEiID6/olad+amhPgMAAQAFjLpN6Knd/7yxWh3mEpFRn+Pui6ypQ07cXb2/vVF/RMxGRv+/vTJ5teZ6Uf4h9v+NSnxcGHR5vsHz5Tn2czSt5npglTV9mEAIARBf19KrVQHaMh5rp2n+FNhugN4wHNUJpRkrPJ1Laao9Dbgm+4BXqtZKK6WYFm78eK1moXiyhq2t3awahaxa+3Fh1fKVXieDwDwPB/lciU+3BgsQNM4AEDTNBhGIRKeiDKk63lMTI6jUq7CMArI6wPx4TcH6Ho+6jiAu/IV7x5ORRjcCizCgNKGf0xdN1ZYcVyQhn9EE3VnLlPasCFlPLKU6Cqt20nHnVXWW63zsSvxQz04HAn6+1LtbCTFcZFdNu3kqf3uledt/lqaJmNDfmf6o+Q891/bvykapOGfqI779mWz+QUAfgIkIqKOOyIlKAAAAABJRU5ErkJggg=='
        self.lock2 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIaSURBVEiJ7ZUxaBNhFMf/312+nheTS3KKokOOJqlTmgulEjd1EQdLLbpolbg7ibviLq5FcAhiMYviVFzaKi6mFYRaN5OcHUwCHto7vcvl8+4cTGK1iL2kY3/b997Hj8fj8R5BlzKlE05MuuuKYtKnVPAJwU4hvg/CmMPZ9oawady8xNhbACAAUEpI19mRo7e+Xpw55EYiO5b+DWeakJ88a4UajTvXvmzOkTKlE9/GMgufi7OHEaDaf+L7OFh61BI/VM/yU3JiXi/OZn1BAADouo6VyioIxyEejwWXEwInnYoI6++PhVxRVHqt0HUd9+cewDAMhMNhTJ8/BzWvBva7UhTYJyqcH+JHesF3a+swDAMAYFkWVipvglfexaO8wG0NjKZGEQ6HAQCUUqQzqYHlABDa+lCUJKZnplB5vYpMJoVTp0/unhwAVDUHVc0NJe3B/f/LnnxP3mXbKAbB8zwsLS6jVtNQOHF82wgPJV9aXMbLF6/AGEOz0UQ8HoeiJPv5odpSq2lgjAH4tYu0uvZHnuOY6wwqLxQm+7tIkiSM57K/xcx1Qlzb/siZZtqLRgPL1byKeCIBra5hPJeFLMsAAN4wQdq2RuYpzVtj6ed68cquXaIDpYet/VXtDP/U85oXfrDvQrU+6aRTkd5FGgTeMCE/LrdGPrVuX7WshX6pZUpVOybd80VRGej6d1ibtO0NwTBvXO501gDgJ7gmwQA4AZCHAAAAAElFTkSuQmCC'
        self.lock3 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ5SURBVEiJrZVNTBNBFMf/s+2w7lqWthqNHtjQFuih2yUEgzf1YjxIkPgRFQ3ePRnvGu/GKzHxQIzECmI8ES+Axot8qAktaTFSVg5CEzfKru62jN31AEUUjG3p7zZvJr95mXl5j2CDBKXthQbpblEQGl1KeZcQlAtxXRDGCpxtL/Grxs1LjL0HAAIAAwHpOjt0+Na3cz0Hij5f2dK/4UwTwZHnOe/y8p1rX1f7SYLS9u/NkdEvfb0HUUG2/8R1sX/gUU74uHDK0xUMDOp9vTGX5wEAuq5janIahOPg9zdULicEhXDIx6fmWrxFQZBLT6HrOu73P4BhGBBFEd1nTkNtUyv2F6V6YI8gc67XU1cKJmdTMAwDAGBZFqYmZyrPfAOHenhua6Ap1ARRFAEAlFKEI6Gq5QDg3bqQ5UZ093Rh8s00IpEQjp84Vjs5AKhqHKoa35W0BPf/I+uk0xkMD40gk5mvrTydzmD4yVO8nXmHocQw5jMfaidPJedgWTYAwLJsJJOp2smVeAyiKAAARFGEosTKkm/70J2IRltx4eJ5pJJzUJQYWqMttZOXLohGW8s9Xpl8JxzHwfjYBLJZDZ1Hj2wr4V3Jx8cm8OrlazDGsLK8Ar/fD1lu3Nwvu853IpvVwBgDsN6LtEXtj32OY8VCtfLOzo7NXiRJEpT47yriWLHg5fL2J840w059fcVytU2FPxCAtqhBiccQDAYBAB7DBMnbGhmktM1qDr/Q+67UbBLtG3iY27ugnfQ8c5yVsz/ZD35hsaMQDvlKE6kaPIaJ4ONEru5z7vZVyxrdTDVBqWo3SPdcQZCrmv5rLE/y9hJvmDcur63NAsAvPAPlbZ7mN2kAAAAASUVORK5CYII='
        self.lock4 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAALISURBVEiJ7ZVBaFN3HMc/7yV/43trX9NEHA7W8JJ2p7SvFNf2VrPI2EHRohetUi9FZKexu2P3sasIHooo68UxRWQX7WRM2lRptPHWpC8t2AYM2pftpel/yfOgyay1WS2exO/tx/fP5//7//nx/Sm80oQQfZU246eqpnV4QgQ8RWG7UjwPRcqKWi4vBlad709IOQugAIy3G9/KfZ+df358eG+1pWXb0DellkqErv1W8C8v/3jm2eoFZUKIvr+7Om89HR35lHfodkt5HnvGrxS0+ew3vsOh9qvF0ZG4FwgAUCwWSU3PoKgqwWDb/7Lydp707ENaDQNd10BRqMSiLYHM4y/8VU2L1L+iWCxy8cIlHMdB13WOHD2E1WttCU7Pprlx/SauW+beX1OcPTdGOByiarTCbi2ien7frvrhuUcZHMcBwHVdUtP3m3adSj3AdcsAOI5DZi7T8GrCF1BfP2xGTXRdB0AIQawz2hQei0URQgCg6zqmaW7w/a8XkUgHR4YPMz01Q2dnlAOJoabwxFdDoEB2PsfgYD8dkc+3hgNYVg+W1dMUWpeqqiSTCZLJxNv9bVF2qI/wDwy+aRTTs2lSqQfEoiaJ5AFUdev7a7Uad25PksvZDAx+uWmEN8Dzdr6RFUuLS6AoJA++fYYB7tye5O4ffyKlZGV5hWAwSCTS0fA3tGXb+UZWSCnJZXNNn53L2UgpgZdZZC/YG3xVldVKvYh3xzEMA3iZFQOD/U3hAwP7G1lkGAbdPfH/wLJa8atr5bxaKsVqra2EwyHOnhsjM5fBNM1NWfGmrF6LYHs79oJNd0+cUCgEgM8poayVbeWqEL1uV+z34uip97aJwuOXC59k7a99v9ZqK8f+lf8Esgv7K7FoS30j7UQ+p0Tol4nCrieFH0677q1GqxNCWOU242dP0yI72v7rck1ZKy8GnNJ3J9fXHwG8AJ/gBT4wSut6AAAAAElFTkSuQmCC'
        self.lock5 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAMjSURBVEiJrZVBbBtFFIa/XXtrdkk2jo1AIBFr7bTxwfZGVWlya40R4kBVKqACShUuVVX1hLgXcUdcKyQOEaLCNBQBQhWXtiAEatyGmNpRXFQ761QisVQLuqbrOFN7OQSbpEmMKflvo/fm2zcz/74n8bfSirK3MaC/31TVIVdRfK4k0ask10USoiHX64u+u/Y7rwsxCyABTA7qp8WTT53545Ujjzf7+nqGPii5ViNw4cuKd2npvbd+v3tWSivK3j93D1+8M3HsCf5DtdvKdXls8pOKeqv4gudQYPBcdeJYzPX5AKhWq2SmryHJMn7/wL+yylaZ7Owv9Os6mqaCJNGIhPt8+bk93qaqhtpXUa1W+fDsR9i2jaZpHH7pRcxRc1twdjbL1199g+PU+enHq5w8dYJgMEBT74dH1JDsej272sm5G3ls2wbAcRwy09e7Vp3JzOA4dQBs2yafy3diLcXjk9cnG2EDTdMAUBSFyHC4KzwSCaMoCgCapmEYxoa4d/0iFBri8JFDTF+9xvBwmIPJA13hyWcPgATFWyXGx/czFHp6eziAaSYwzURXaFuyLJNKJUmlklvHe6IA8/MFps5foFC42euW3uDz8wWmPvucmes/cz49xc3CrzsHz+fmOq5wnDq5da743/B4Irb2g7Dming81hN804NupWh0hKOvvUo+N0c8HmMkumfn4O0PRKMjvaZvDc/OZslkZoiEDZKpg8jy9jfXarW4fOkKpZLF2Pgzmyy8AV62yp1ecXvxNkgSqee29jDA5UtX+P67HxBCsLy0jN/vJxQa6sQ3lGVZ5Y4rhBCUiqWuxy6VLIQQwFovshasDXFZFs1GexGLx9B1HVhzxdj4/q7wsbF9nV6k6zrxxD8ukkWz4ZVX6mW5Vou0+vsJBgOcPHWCfC6PYRibesWDMkdN/IODWAsW8USMQCAAgMeuIa3ULemcoow6uyPfVife3LFJFJz8uPJo0Xre80WrtfzyfXHPV1zY14iE+9oT6WHksWsEPk1Xdv1Wefe441zslJpWFLM+oH/gqmrooab/qliRVuqLPrv29hurqzcA/gIjvSmrbKxhRgAAAABJRU5ErkJggg=='
        self.lock6 = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAXCAYAAADgKtSgAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAOISURBVEiJrZVRTBt1HMc/d+VWepSjFCNgIre24LZAuWZhwNzDhjXGB5e56IviRGPIsvhkfNf4bnxdTHwgZmRkilFjFqNu0+h0KyPtRklg0nJlyYDERnctvStnWx+QSoFWXPy+/e/7z+e++f9//99P4G9NSNLhfJPyfsHl6ihJkrMkCOxVQqmEYNt50TSXnA+Mt1+y7SiAADDWrLxptz/2zh8vnn604HbvGbpdYiaDd/Lz1brl5fde+/3BeWFCkg5nuzov/zYy3Mp/SFtVpRKPjF1YdS0knnWc9DaPp0eGe0pOJwDpdJrIzSkEUcTjafpXVkpPEYveplFRkGUXCAL5gN/tjM8+UVdwudTNo0in03x4/iMMw0CWZU49/xxaSKsKjkVjfPnFV+RyJj9fv8HZc6O0tHgpKI1Q71LFUp1j3+bmmTtxDMMAIJfLEbl5q2bqSGSaXM4EwDAM4jPxsleUHE5x62af34csywBIkkSg018THgj4kSQJAFmW8fl8FX7d1oWqdnDq9Elu3piis9PPiaHjNeFDTx0HARILSQYH++lQH68OB9C0XjSttyZ0U6IoEg4PEQ4P7e5v/7CYXOSTS5PEorf39INoNManlyZJ6akdXkXy5fvLjF+4SDa7Rjw+i2maHH1ysCr4+k+/8O0332FZFnNzd3lj9HXa29t2Tz4/f5dsdg2AvJVnZma2ZurZ+CyWZQGQzWaZn5uv8CvgBw4ewO1uAKC+vp5gsLsmvDvYjbN+4/G53W4OHTpY4VccS3t7G2deHWZqapqurk60UO2LPXbsKA0NMgu/JjjS30drW2t1OIC6X0Xdr9aEblUopBGq8op3wGPRGJHINAG/j6HwCURxR0GVVSwWuXrlGsmkzsDgkR0lXAFP6alyr7i3dA8EgfDTu9cwwNUr1/jh+x+xbZuV5RU8Hg+q2lH2K2LpeqrcK2zbJplIVgUDJJM6tm0DG71IX9QrfFG0C/nNRU+wB0VRgI1eMTDYXxM+MNBX7kWKohDs7fkHbBfydaJlpsRMJlBsbKSlxcvZc6PEZ+L4fL4dvWK7tJCGp7kZfVEn2NuD1+sFwGFkECxTF8YlKZTrCnydHnnlf5tELWMfrzYk9GccnxWLKy/8aa85E4t9+YDfvTmRHkYOI4P34sTqvvur757J5S6Xo05IkmY2KR+UXC71oab/um0JlrnkNDJvvby+fgfgLxhlT0CvnDboAAAAAElFTkSuQmCC'
        self.up = b'iVBORw0KGgoAAAANSUhEUgAAABcAAAAKCAYAAABfYsXlAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAD6SURBVCiRtdFBSgMxFMbxfyZxQj1C3Vbs7KpXEN2oNxBdii20Ct5BkCIewaonUCky0iuoJ6g7S8etZZowGHeFYRrKgP2WL8kvj/dEPOg7lpQAWBbugjK3k+S7lK4Wfu8c8csrvd4Dk58JUVSnfdaiulZdiIt40P8FxLzD4fCTq8suX6MR03QKgJQSpST7B3scHR9SWa14+5qLG2O5u73n6fEZYyzOFdeitUatKE6bJ+zsbiNEob8i/v72wXX3hvE4QesQKf2Ts9aSZRm19RrtTot6tJHDcy+NsQCcX3S8oC9pmmKtJQzDWS2Hax2yudUoDfsS4FnmP0T8AVnYVU+ZVHgeAAAAAElFTkSuQmCC'
        self.menubar1 = b'iVBORw0KGgoAAAANSUhEUgAAAAwAAAATCAYAAACk9eypAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAABxJREFUKJFjlJGR+c9AAmAiRfGohlENoxoo1AAAFTwBedVtAcUAAAAASUVORK5CYII='
        self.menubar2 = b'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'
        self.menubar_CLT_hover = b'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'
        self.menubar_CLT = b'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'
        self.author_hover = b'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'
        self.menubar1_r = b'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'
        self.author = b'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'
        self.minimize = b'iVBORw0KGgoAAAANSUhEUgAAACYAAAATCAYAAAD8in+wAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAFhJREFUSInt1MEJwDAMQ1G5dP9ltJ+dCQqRIDQHfcgtgYcJLgCDC3v+BnwVmFpgaoGpve7Dqtq6N+OtSWtiJNHdW4ekBSuYm//0xGzY6a79/IGpBaYWmNoCy00rGVzOAC4AAAAASUVORK5CYII='
        self.exit = b'iVBORw0KGgoAAAANSUhEUgAAACYAAAATCAYAAAD8in+wAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAOVJREFUSIntlDGKhDAUhv8JKVLkDtMKlraWAU8QyJG8gm2EXCBgEeztPYN4A8Xun2YXhl220GVmZfGDv8rLy/fgkRsA4oSIvxb4iUtsL5fYXg6Jaa1fUvsV7k0IgSklOueolPp2rpSic44pJYYQdvf/yP5LQggaY+i95zzPbJqGZVkyz3PWdc1pmhhjpLWWUsr3iT3nfr+zbVsuy8Jt29h1HbMs+1VPADy0Y0IIGGPgvccwDFjXFVVVoSgKjOOIvu8RY4S1FlLKI08AR6Y57Y5prV9S+5zbp93Z+F8f7Du4xPZyWrEHg9MAni6rng8AAAAASUVORK5CYII='
        self.minimize_hover = b'iVBORw0KGgoAAAANSUhEUgAAACYAAAATCAYAAAD8in+wAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAMNJREFUSIntljEKxCAQRb9hO0Eh2qTJDXIKr+KxvEpOYmcTEGwE62y3rJEFkwXXhbzyMzgPGYYhAHZ0yOMYcM4xjmNTCe89UkpZlolJKWGtBaW0qViMEcuyYNu2Vza8F8zz3FwKABhjmKYpy4YPtT/nFjtLt2LFuqhl3+vWHyHk0vuXxLTWWNe1qlYpBWPM6R6XxIwxff7YNw1r6Xb4b7Gz/IeYc644P1qQUoJzLssIDociYwxCiJZeCCEgxphlhVgvPAFHfjH+GTQ4cAAAAABJRU5ErkJggg=='
        self.exit_hover = b'iVBORw0KGgoAAAANSUhEUgAAACYAAAATCAYAAAD8in+wAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAAZhJREFUSIndlk1LAlEUhp+5CqOTBcrURqhf0KpVuIkwgpCohSDRB/QLot8Qrlq0LggsaFNgIASZuAuXQRG4aRUuKkkCGx3UmRZROGOhDTSF7+6e+97Dwz2Hc68EmPxDee2BQQRBPK5ClGmi2e7HAhbCQ4FRFCRXwaoYTHHPA63PmGg3hPG6DgUQQDBiK574xvvn6i8wKaD8irddjsCCu0nUbAolEUPyyZ0wPhklEUPNpgjuJh2BSbTNsXFkzgh3PyUE8vQkA6uLyNEI9Uwe7TCNUXlBWVlEWV6gcXXL60GaWvocmq2uKecocYP+ue6YYz3JMNBzl+i5S7xjYYa2NlHPU+AR6PkCT9EVmsU7R6k/5Kz5hUCORggdbDNcOMHU6pRn13icmKdxXWQ4d4ia2cMfnwOvs2HtqJShox2EGkTbP6Z2eoFZ1y37kk/GvzCDsh7HKFd4XtromtNeSkdgUkDBrGpdfT/x2sEclbJXqJ9629VfA9YNWcBKX3w/3JCGSYmmJWZpfnh/6UMu/8eeaVHFsMQ6wP6L3gCof32hmi+c+gAAAABJRU5ErkJggg=='

class Mainframe:
    def __init__(self):
        """
        The main object.  
        Houses everything and has methods that facilitate most of the directions given by the EventHandler.
        """
        print('[LOG] Initializing frame... ', end='')
        # Inheritance
        self.window: sg.Window = None
        self.values: dict = {}
        
        # Self
        self.images = ImageData()

        # Initialize the maestro, an EventHandler
        self.maestro: EventHandler = None

        # Initializing frame variables
        self.preset_list: list[str] = ['Fair', 'Sloped', 'Valley', 'Hill', 'Alternating']
        self.presets: dict = {
               'Fair': [float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), 100 - float(500 / 6)],
               'Sloped': [47, 23, 16, 8, 4, 2],
               'Valley': [40, 8, 2, 3, 9, 38],
               'Hill': [2, 12, 40, 38, 7, 1],
               'Alternating': [32, 0, 32, 0, 32, 4],
        }
        self.dice: int = 1  # number of dice

        # Controlling variables
        self.update_interval: int = 64        # Controls framerate / speed of simulation
        self.simulate: bool = False           # Turns the simulation on or off (pause/play)
        self.matching_graphs: bool = False    # If the graphs match, we can select and compare columns between sim. and conv.

        # Graph dimensions and margins
        # Simulation graph
        self.sim_margins: list[list[int]] = [[100, 20], [75, 50]]  # (left, right), (bottom, top)
        self.sim_graph_size: tuple[int, int] = (1000, 10000)       # The height extends far past what is shown to allow for many rolls, the values get overridden in make_window
        self.sim_viewing_height: int = None                        # Height of the simulation graph that gets displayed
        self.sim_graph: sg.Graph = None                            # Gets initialized by make_window.py in the update_window() function
        # Convolution graph
        self.con_margins: list[list[int]] = [[10, 10], [25, 10]]   # (left, right), (bottom, top)
        self.con_graph_size: tuple[int, int] = (450, 325)          # Hardcoded size, doesn't change
        self.con_graph: sg.Graph = None                            # Gets initialized by make_window.py in the update_window() function

        # Single Die Distribution
        self.locked_values: list[int] = [0] * 6     # List to hold the values that each slider may be locked at.
        self.locks: list[bool] = [False] * 6        # List of bools to keep track of which sliders are locked 
        self.die_distribution: list[float | int] = self.random_distribution(get_var=True)  # distribution that sums to 100
        print(f"Starting die distribution: {self.die_distribution}", end='... ')
        self.mean, self.deviation = self.mean_and_deviation([value / 100 for value in self.die_distribution], update=False)  # Type: float, float
        
        # Initialize Simulation 
        self.sim: Simulation = None  # Gets initialized by the EventHandler, maestro

        # Initialize Convolution
        self.convolution_title = f' The Probability Distribution for the Sum of {self.dice} Dice '
        self.convolution: Convolution = Convolution(self)  # Requires a frame as a parameter
        self.convolution_display_ids: list = []            # Figure ID's for the figures of the bar display method on the convolution graph

        print(f'Complete!\n')

    
    def resize_graphs(self):
        """
        The graphs do not actually get resized.  When initialized, the graph has a width and view height that fill the available screen size. 
        This function re-defines the allowed drawing area of the simulation to fit in the new window size.
        """
        window_size = self.window.size
        self.sim_graph_size = (window_size[0] - 475, 10_000)
        self.sim_viewing_height = window_size[1] - 105  # the vertical number of pixels of the sim graph that get displayed
        if self.sim:
            self.sim.top_right = (self.sim_graph_size[0] - sum(self.sim_margins[0]), self.sim_graph_size[1] - sum(self.sim_margins[1]))
        

    def random_distribution(self, get_var=False):
        """
        Creates a randomized probability distribution (in percent) that allows for some values to remain fixed.
        As long as the lengths of `locked_values` and `locks` are equal, can create a distribution for arbitrarily many outcomes.
        :param get_var: Type - bool: If True, returns a list, else sets self.die_distribution to the created list.
        """
        locked_sum = sum(self.locked_values)
        sum_to = 100 - locked_sum
        random_values = []
        for locked in self.locks:  # find the unlocked faces and create a random number for each one found
            if not locked:
                random_values.append(random.random())
        total = sum(random_values)
        # Normalize the random values so they sum to the correct amount. Scaling factor = (desired sum) / (total of randomized numbers)
        normalized_values = [int((sum_to * value) / total) for value in random_values]
        normalized_values[-1] = int(sum_to - sum(normalized_values[:-1]))  # trim off any rounding error from the final entry

        # build a valid, and ordered, distribution from the randomized values and the locked values
        valid_distribution = []
        unlock_counter = 0
        for lock_counter, locked in enumerate(self.locks):
            if locked:
                valid_distribution.append(int(self.locked_values[lock_counter]))
            else:
                valid_distribution.append(normalized_values[unlock_counter])
                unlock_counter += 1

        if get_var:
            return valid_distribution
        else:
            self.die_distribution = valid_distribution


    def mean_and_deviation(self, distribution=None, update=True):
        """
        Calculate the mean and standard deviation of the given distribution. 
        :param distribution: Type - list[float|int]: If None, uses self.die_distribution
        :param update: Type - bool: If True, will update the mean and deviation display on the frame.
        """
        get_vars = True
        if distribution is None:
            distribution = self.die_distribution
            get_vars = False
        if abs(sum(distribution) - 100) < 10:
            # Convert a distribution given in percentages to decimal
            valid_distribution = [item / sum(distribution) for item in distribution]
            valid_distribution[-1] = 1 - sum(valid_distribution[:-1])
            distribution = valid_distribution
        mean = 0
        for x, y in enumerate(distribution, 1):
            mean += x * y
        variance = 0
        # for x in range(1, 7):
        for x, y in enumerate(distribution, 1):
            variance += y * ((x - mean) ** 2)
        standard_deviation = variance ** .5
        
        if update:
            self.window['mean'].update(f'Mean: {mean:.2f}')
            self.window['deviation'].update(f'Standard Deviation: {standard_deviation:.2f}')
        if get_vars:
            return mean, standard_deviation
        else: self.mean, self.deviation = mean, standard_deviation

    
    def activate_hit_detect(self, click, graph: sg.Graph, event: str, objects: list[object], 
                            prev_selection: tuple[int, object] = (None, None), offset: tuple[int, int] = (0, 0)): 
        """
        Searches through the given list of objects to see if the click location is inside of one of their hitboxes.
        If an object is it, its display() method is called and a selection box is drawn on top of it.
        Returns the object and its ID, or None.

        :param click: Type - tuple: graph coordinates of the click
        :param graph: Type - PySimpleGUI.Graph: Required to know which graph to draw the selection box
        :param event: Type - str: Name of the graph. Used to check for bin selection of the Sim. graph
        :param objects: Type - list[object]: List of objects to search through. Either Roll or Bar objects.
        :param prev_selection: Type - tuple[int, object]: The ID of the previous selection box and the previously selected object.
                                                          - Only the ID is actually used atm.
        :param offset: Type - tuple: Horizontal and vertical offset for hit detection search. Given as parameters to Object.is_hit(...) method
        """
        selection_id = prev_selection[0]
        if selection_id:  # delete drawings 
            graph.delete_figure(selection_id)

        found = False
        print(f"Clicked {event}: {click}, \nLooking... ", end="")

        # clicked the simulation graph below the x axis, select the bin if the graphs match.
        if event == 'simulation graph' and click[1] < 0 and self.matching_graphs:
            if self.convolution.selection_box_id:  # delete the selection box for any currently selected convolution bar
                self.con_graph.delete_figure(self.convolution.selection_box_id)
            for i, bin in enumerate(self.sim.possible_outcomes):
                if not found:
                    if click[0] in range(self.sim.box_width * i, self.sim.box_width * (i + 1)):
                        found = True
                        hit_bin: Bar = self.convolution.bins[i]
                        hit_bin.display()
                        self.convolution.selection_box_id = self.con_graph.draw_rectangle(hit_bin.hitbox[0], hit_bin.hitbox[1], 'magenta')
                        print(f'found: {hit_bin}\n')

        # only search for objects if the click is in the graphing region
        elif click[0] > 0 and click[1] > 0:  
            for Object in objects:
                if not found:
                    if Object.is_hit(click, xoffset=offset[0], yoffset=offset[1]):
                        found = True
                        selection_id = graph.draw_rectangle(Object.hitbox[0], Object.hitbox[1], 'magenta')
                        print(f'found: {Object}\n')
                        Object.display()
                        return selection_id, Object
                    
        if not found:
            print('found nothing.\n')
            if self.sim:
                self.sim.deselect_all_bins()


    def add_preset(self, new_preset: str):
        self.preset_list.append(new_preset)
        self.presets[new_preset] = self.die_distribution
        self.window['preset'].update(values=self.preset_list)
        print(f"[LOG] New Preset added.\n{new_preset} : {self.presets[new_preset]}")

    
    def activate_lock(self, active_lock):
        self.locked_values[active_lock - 1] = self.values[f'face{active_lock}']
        self.locks[active_lock - 1] = not self.locks[active_lock - 1]
        if self.locks[active_lock - 1]:
            b64_image_data = getattr(self.images, f'lock{active_lock}')
            self.window[f'lock{active_lock}'].update(image_data=b64_image_data)
        else:
            b64_image_data = getattr(self.images, f'die{active_lock}')
            self.window[f'lock{active_lock}'].update(image_data=b64_image_data)
            self.locked_values[active_lock - 1] = 0


    def set_sliders_to(self, slider_values, reset_locks=False):
        """
        Used to set all sliders to pre-decided values. Used by 'Randomize' event and `set_preset`
        :param slider_values: Type: list[inf|float] length=6: Must be present. Values to set the sliders to.
        :param reset_locks: If True, unlocks all sliders and resets the images
        """
        for i in range(1, 7):  # Update sliders and locks
            if self.locks[i - 1] and reset_locks is True:  # Reset locks
                self.locks[i - 1] = False
                self.locked_values[i - 1] = 0
                b64_image_data = getattr(self.images, f'die{i}')
                self.window[f'lock{i}'].update(image_data=b64_image_data)
            self.values[f'face{i}'] = slider_values[i - 1]
            self.window[f'face{i}'].update(self.values[f'face{i}'])

        self.die_distribution = slider_values
        self.mean_and_deviation(slider_values)
        self.convolution = Convolution(self)


    def activate_slider(self, event, active_face=None, set_to_value=None):
        """
        Moving one slider means moving all the other sliders as well. 
        This function facilitates that. 
        """
        if set_to_value is None:
            set_to_value = self.values[event]
        if active_face is None:
            active_face = int(event[-1])
        self.values[event] = set_to_value

        # If the face is not locked, accept the input value and adjust other faces
        if not self.locks[active_face - 1]:  
            active_slider_key = event
            active_slider_value = self.values[event]
            slider_values = [self.values[f'face{i}'] for i in range(1, 7)]
            total = sum(slider_values)
            locked_sum = sum(self.locked_values)
            unlocked_sum = total - active_slider_value - locked_sum

            # Scale the other sliders.

            # Scaling is required and there is at least 1 locked slider.
            if total != 100 and unlocked_sum != 0:  
                # Calculate the scaling factor to preserve the relative positions
                scaling_factor = (100 - active_slider_value - locked_sum) / unlocked_sum

                # Scale all unlocked sliders while preserving relative positions
                for i in range(1, 7):
                    if active_slider_key == f'face{i}' or self.locks[i - 1]:
                        # Skip the actively modified or locked slider
                        continue
                    else:
                        slider_values[i - 1] = int(slider_values[i - 1] * scaling_factor)
                        self.window[f'face{i}'].update(slider_values[i - 1])

                # Adjust active slider to ensure the sum is 100
                total = sum(slider_values)
                adjustment = 100 - total
                slider_values[active_face - 1] += adjustment
                self.window[active_slider_key].update(slider_values[active_face - 1])
  
            # The unlocked sliders were all 0 and the active slider was reduced; increase an unlocked slider.
            elif unlocked_sum == 0 and total < 100:
                next_unlocked_face = None
                for i in range(1, 6):
                    # Find an unlocked slider. If there are none, lock the active slider.
                    next_face = ((active_face - 1) + i) % 6
                    if self.locks[next_face]:  # Skip locked sliders.
                        next_unlocked_face = None
                        continue
                    else:
                        next_unlocked_face = next_face + 1
                        break
                
                # No unlocked faces were found; lock active face in place.
                if next_unlocked_face is None: 
                    adjustment = 100 - total
                    slider_values[active_face - 1] += adjustment
                    self.window[active_slider_key].update(slider_values[active_face - 1])
                # Found a slider to adjust.
                else:
                    self.values[f'face{next_unlocked_face}'] = 100 - active_slider_value
                    self.window[f'face{next_unlocked_face}'].update(self.values[f'face{next_unlocked_face}'])

            # The unlocked sliders were all 0 and the active slider was increased; decrease active slider.
            elif unlocked_sum == 0 and total > 100:
                adjustment = 100 - total
                slider_values[active_face - 1] += adjustment
                self.window[active_slider_key].update(slider_values[active_face - 1])

            # Finished moving, update related objects.
            self.mean_and_deviation(slider_values)
            self.die_distribution = [_ for _ in slider_values]
            self.convolution = Convolution(self)
            self.window['preset'].update(value='')

        else:  # Slider is locked, keep value constant
            self.values[event] = self.locked_values[int(event[-1]) - 1]
            self.window[event].update(self.values[event])


    def dice_change(self, value=None):
        """
        Method to keep track of the amount of dice entered. Only allows positive integers to be entered.
        Updates the title of the Convolution graph and creates a new Convolution. 
        """
        if value is None:
            value = self.dice
        # inheritance
        try:
            if value == '':
                raise Exception
            value = int(value)
            self.dice = value if value > 0 else 1
            self.window['dice'].update(value=self.dice)
            self.window['dist tab'].update(title=f' The Probability Distribution for the Sum of {self.dice} Dice ')
            self.convolution = Convolution(self)
        except ValueError:
            raise ValueError('The number of dice must be a non-negative integer.')
        except Exception:
            self.dice = self.dice
            print(self.dice)


# ----------------------------------------------------------------------------------------------------------------------
#  .d8888b.                                      888          888    d8b                   
# d88P  Y88b                                     888          888    Y8P                   
# 888    888                                     888          888                          
# 888         .d88b.  88888b.  888  888  .d88b.  888 888  888 888888 888  .d88b.  88888b.  
# 888        d88""88b 888 "88b 888  888 d88""88b 888 888  888 888    888 d88""88b 888 "88b 
# 888    888 888  888 888  888 Y88  88P 888  888 888 888  888 888    888 888  888 888  888 
# Y88b  d88P Y88..88P 888  888  Y8bd8P  Y88..88P 888 Y88b 888 Y88b.  888 Y88..88P 888  888 
#  "Y8888P"   "Y88P"  888  888   Y88P    "Y88P"  888  "Y88888  "Y888 888  "Y88P"  888  888
#
# - An object that lives in a `mainframe`. It creates a convoluted probability distribution out of `bar` objects
# ----------------------------------------------------------------------------------------------------------------------
class Convolution:
    def __init__(self, frame: Mainframe):
        """
        An object that lives in a `Mainframe`. It creates a convoluted probability distribution out of `Bar` objects
        """
        # Inheritance
        if frame.con_graph is None:  # When the frame is instantiated, the window and graph have not yet been created.
            print('Making Convolution', end='... ')
        self.f: Mainframe = frame
        self.graph: sg.Graph = frame.con_graph
        self.die_dist: list[int|float] = frame.die_distribution
        # Ensure the die distribution has a sum of 1. The frame uses a distribution that sums to 100.
        if sum(self.die_dist) != 1:
            self.die_dist = [x / sum(self.die_dist) for x in self.die_dist]
        else:
            self.die_dist = self.die_dist
        self.number_of_dice = self.f.dice

        # If a new convolution is being made, then the theoretical prediction won't match the simulation, no point comparing columns.
        self.f.matching_graphs = False
        if frame.sim:  
            self.f.sim.deselect_all_bins()

       # Self
        self.possible_outcomes = list(range(self.number_of_dice, (6 * self.number_of_dice) + 1))  # all possible outcomes
        self.conv_dist = self.create_convoluted_distribution(get_var=True)
        self.highest_point: int | float = None  # largest y-value that is allowed to draw bars on
        self.bin_width = 1
        self.scalar = 1                         # Scaling factor used to scale the pixel size of each probability
        self.bins: list[Bar] = []               # list of all the bars
        if self.graph:
            # The make_bars() method does many things. It finds an appropriate box size, creates the drawing area, and trims the outcomes.
            self.make_bars()  

        # Selection IDs and control
        self.current_selection = None       # The bin number of the currently selected bin
        self.selection_box_id = None        # Needs to be tracked separately so that the Simulation can delete it.
        self.selected_bar_display_ids = []  # The figures displayed on the convolution graph
        

    def create_convoluted_distribution(self, dice=None, get_var=False):
        """
        Uses numpy to convolve the die distribution with itself `number_of_dice` times.
        """
        if dice is None:
            dice = int(self.number_of_dice)
        convoluted_distribution = self.die_dist
        for _ in range(dice - 1):
            convoluted_distribution = np.convolve(convoluted_distribution, self.die_dist)
        if get_var:
            return convoluted_distribution
        else: 
            self.conv_dist = convoluted_distribution


    def trim_outcomes(self):
        """
        Trims the list of all possible outcomes. Only allows outcomes that would use more than 0.1 px to display.
        Searches from both left and right for the first thing that would require more than 0.1 px to display. 
        """
        feasible_outcomes = self.possible_outcomes
        distribution = self.conv_dist
        
        tol = 0.1
        found = False
        for i, x in enumerate(distribution):
            if not found:
                if x * self.scalar > tol:
                    left_border_index = i
                    found = True
        
        found = False
        for i, x in enumerate(reversed(distribution)):
            if not found:
                if x * self.scalar > tol:
                    right_border_index = len(distribution) - i - 1
                    found = True
        
        feasible_outcomes = feasible_outcomes[left_border_index : right_border_index + 1]
        self.possible_outcomes = feasible_outcomes
        self.conv_dist = distribution[left_border_index : right_border_index + 1]
        return
    
    
    def drawing_area(self):
        self.graph.draw_rectangle((0, 0), self.top_right)
        # Draw x-axis tick marks and labels
        x_tick_label_diff = len(self.possible_outcomes) // 5  # ensures there are always 6 or fewer tick labels
        x_tick_label_diff = 1 if x_tick_label_diff < 1 else x_tick_label_diff
        for i, bin in enumerate(self.possible_outcomes):
            box_center = self.bin_width * (i + 0.5)
            self.graph.draw_line((box_center, -1), (box_center, -5))   # box_center = self.box_width * (i + 0.5)
            if i % x_tick_label_diff == 0:
                self.graph.draw_text(f'{bin}', location=(box_center, -10))
 
    
    def find_sizes(self):
        highest_probability = max(self.conv_dist)
        self.highest_point = self.top_right[1] - 45
        self.scalar = self.highest_point / highest_probability
        if self.number_of_dice > 14:
            self.trim_outcomes()
        bins = len(self.conv_dist)
        self.bin_width = self.top_right[0] // bins
    

    def make_bars(self):
        self.graph.erase()
        self.bins: list[Bar] = []
        self.graph = self.f.con_graph
        self.top_right = (self.f.con_graph_size[0] - sum(self.f.con_margins[0]), self.f.con_graph_size[1] - sum(self.f.con_margins[1]))
        # find grid points
        self.find_sizes()
        self.drawing_area()
        for i, x in enumerate(self.conv_dist):
            probability = x
            height = x * self.scalar
            x_location = i * self.bin_width
            bin_number = i + self.possible_outcomes[0]
            new_bar = Bar(conv=self, bin=bin_number, prob=probability, size=(self.bin_width, height), coord=x_location)
            self.bins.append(new_bar)
        tallest_bar = max(self.bins)
        x = tallest_bar.x_coord + self.bin_width + 1
        self.graph.draw_line((x, tallest_bar.size[1]), (self.top_right[0], tallest_bar.size[1]), color='#dcdcdc')
        self.graph.draw_text(text=f"p = {tallest_bar.probability:.4f}", location=(self.top_right[0] - 40, tallest_bar.size[1] + 10), font='_ 11 bold')


    def delete_ids(self, id_list=None):
        if id_list is None:
            for id in self.selected_bar_display_ids:
                self.graph.delete_figure(id)
                self.selected_bar_display_ids = []
        else:
            for id in id_list:
                self.graph.delete_figure(id)
            return []    
        
  

# ----------------------------------------------------------------------------------------------------------------------
# 8888888b.  d8b          8888888888                        
# 888  "Y88b Y8P          888                               
# 888    888              888                               
# 888    888 888  .d88b.  8888888  8888b.   .d8888b .d88b.  
# 888    888 888 d8P  Y8b 888         "88b d88P"   d8P  Y8b 
# 888    888 888 88888888 888     .d888888 888     88888888 
# 888  .d88P 888 Y8b.     888     888  888 Y88b.   Y8b.     
# 8888888P"  888  "Y8888  888     "Y888888  "Y8888P "Y8888 
#
# - used by the simulation to display each rolled die on the left side
# ----------------------------------------------------------------------------------------------------------------------
class DieFace:
    def __init__(self, graph: sg.Graph, images, stack_position, x=-73, y=55, y_sep=40):
        """
        Each DieFace knows all 6 die face images and can swap between them.
        """
        self.stack_position = stack_position
        self.face_number = 1
        self.graph = graph
        self.location = (x, (self.stack_position * y_sep) + y)
        self.images = {
            1: images.die1,
            2: images.die2,
            3: images.die3,
            4: images.die4,
            5: images.die5,
            6: images.die6,
        }
        self.image_id = None
        self.image_data = self.set_image()

    def erase(self):
        self.graph.delete_figure(self.image_id)
        self.image_id = None

    def set_image(self, number = None):
        if number:
            self.face_number = number
        if self.image_id is not None:
            self.erase()
        self.image_data = self.images[self.face_number]
        self.image_id = self.graph.draw_image(data=self.image_data, location=self.location)


# ----------------------------------------------------------------------------------------------------------------------
#  .d8888b.  d8b                        888          888    d8b                   
# d88P  Y88b Y8P                        888          888    Y8P                   
# Y88b.                                 888          888                          
#  "Y888b.   888 88888b.d88b.  888  888 888  8888b.  888888 888  .d88b.  88888b.  
#     "Y88b. 888 888 "888 "88b 888  888 888     "88b 888    888 d88""88b 888 "88b 
#       "888 888 888  888  888 888  888 888 .d888888 888    888 888  888 888  888 
# Y88b  d88P 888 888  888  888 Y88b 888 888 888  888 Y88b.  888 Y88..88P 888  888 
#  "Y8888P"  888 888  888  888  "Y88888 888 "Y888888  "Y888 888  "Y88P"  888  888
#
# - Creates `roll` objects and draws them on the graph according to their sum, frequency, and size.
# ----------------------------------------------------------------------------------------------------------------------
class Simulation:
    def __init__(self, frame: Mainframe):
        print('\nBeginning the simulation, enjoy!')
        # Inheritance
        try:
            self.f: Mainframe = frame
            self.graph: sg.Graph = self.f.window['simulation graph']
            self.dist: list[float] = [x / 100 for x in self.f.die_distribution]  # die distribution, normalized to 1
            self.number_of_dice: int = int(self.f.dice)
            self.number_of_rolls: int = int(self.f.values['rolls'])
            if int(self.number_of_rolls) < 1:
                raise Exception
        except Exception:
            print("Cancelling... Could not gather the required inputs.")
            raise ValueError("The number of rolls must be greater than zero.")
        except:
            print("Cancelling... Could not gather the required inputs.")
            raise ValueError("Inputs must be positive integers.")
        
        # Self
        self.graph.erase()
        self.f.window['sim column'].Widget.canvas.yview_moveto(1.0)  # adjust the graph slider to be at the bottom
        self.f.window['Pause'].update(text='Pause')
        self.trial_number = 1
        self.f.matching_graphs = True

        self.possible_outcomes = self.f.convolution.possible_outcomes  # Must have own copy so that the convolution is free to change
        self.convolution: list[float] = self.f.convolution.conv_dist  # the distribution as a list, not the entire object
        self.outcome_counter: dict[int, int] = {outcome: 0 for outcome in self.possible_outcomes}
        self.partition = self.make_partition()  # partition the closed set [0, 1] according to the die distribution, used for rolling

        # Possible redundancy, but we keep two copies of all the rolls.  One is a list ordered by trial number,
        #   the other is a dictionary with a key for each possible outcome.
        # The list is used for hit detection, the dictionary is used for column selection.
        # Hit detection could be optimized to use the dictionary and only search the bins of the corresponding x-range but would make the function less general.
        self.rolls: list[Roll] = []
        self.bin_dictionary: dict[int, list[Roll]] = {outcome: [] for outcome in self.possible_outcomes}  # for bin, outcomes in self.bin_dictionary.items(): ...

        # Drawing area from (0, 0) to (xMax - left_margin - right_margin, yMax - top_margin - bottom_margin)
        self.top_right = (self.f.sim_graph_size[0] - sum(self.f.sim_margins[0]),  # x-coord
                          self.f.sim_graph_size[1] - sum(self.f.sim_margins[1]))  # y-coord
        self.box_width, self.box_height = self.find_box_size()
        self.drawing_area()  # Requires knowledge of the box sizes for x-tick & y-tick locations.
        self.die_faces: list[DieFace] = None  # The DieFace objects that display the current, or currently displaying roll.
        self.draw_dice()                      # Populates `self.die_faces` and draws them.

        # Display
        self.selection_box_id = None
        self.display_ids: list = []
        self.column_outline_ids = []
        self.displaying_roll = False
        self.selected_bin = self.f.convolution.current_selection
        if self.selected_bin:
            self.draw_column_outlines(self.selected_bin - self.possible_outcomes[0])


    def drawing_area(self):
        self.graph.draw_rectangle((0,0), self.top_right)

        # Draw y-axis tick marks, labels, and grid lines
        y_tick_diff = self.number_of_rolls // 15 
        y_tick_diff = round(y_tick_diff / 5) * 5 if self.number_of_rolls > 44 else 5  # closest multiple of 5 to one fifteenth of the max rolls
        delta_y = y_tick_diff * self.box_height  # height difference in pixels
        y_tick_height = 0
        y_tick = 0
        while y_tick_height < self.top_right[1]:
            # format the tick label
            string_length = len(str(self.number_of_rolls)) if self.number_of_rolls > 100 else 3
            tick_string = f'{y_tick:>{string_length}}'
            # drawing
            self.graph.draw_line((-8, y_tick_height), (0, y_tick_height))
            self.graph.draw_line((0, y_tick_height), (self.top_right[0], y_tick_height), color='#dcdcdc')
            self.graph.draw_text(tick_string, location=(-(len(tick_string) * 6.33) , y_tick_height))  # 6.33 is an approximate conversion factor for 10pt to px
            y_tick_height += delta_y
            y_tick += y_tick_diff

        # Draw x-axis tick marks and labels
        # X-tick labels is tricky since the number of outcomes is no longer predictable (we trim the outliers).
        # Without trimming, the range of outcomes is [n, 6n], meaning the difference is always divisible by 5.
        x_tick_diff = len(self.possible_outcomes) // 5  # ensures there are a maximum of 6 tick labels, minimum 5.
        for i, bin in enumerate(self.possible_outcomes):
            box_center = self.box_width * (i + 0.5)
            self.graph.draw_line((box_center, -1), (box_center, -10))
            if i % x_tick_diff == 0:
                self.graph.draw_text(f'{bin}', location=(box_center, -15))

    
    def draw_column_outlines(self, bin_number):
        self.column_outline_ids = self.delete_ids(self.column_outline_ids)
        x1 = (bin_number) * self.box_width
        x2 = (bin_number + 1) * self.box_width
        y = self.top_right[1]
        self.column_outline_ids.append(self.graph.draw_line((x1, 0), (x1, y), color='magenta'))
        self.column_outline_ids.append(self.graph.draw_line((x2, 0), (x2, y), color='magenta'))


    def select_bin(self, previous_bin):
        if previous_bin:
            for roll in self.bin_dictionary[previous_bin]:
                self.graph.Widget.itemconfig(roll.id, fill='cyan')
        for roll in self.bin_dictionary[self.selected_bin]:
            self.graph.Widget.itemconfig(roll.id, fill='Royal Blue')
        self.graph.Widget.itemconfig(self.rolls[-1], fill='green')  # ensure the final roll is still green

    
    def deselect_all_bins(self):
        if self.selected_bin:  # ensure that a bin was actually selected
            self.selected_bin = None
            for roll in self.rolls:
                self.graph.Widget.itemconfig(roll.id, fill='cyan')
            self.column_outline_ids = self.delete_ids(self.column_outline_ids)
        if self.f.convolution.selection_box_id:
            self.f.con_graph.delete_figure(self.f.convolution.selection_box_id)
            self.f.convolution.selection_box_id = None
        self.graph.Widget.itemconfig(self.rolls[-1], fill='green')  # ensure the final roll is still green


    def delete_ids(self, id_list=None):
        if id_list is None:
            for id in self.display_ids:
                self.graph.delete_figure(id)
                self.display_ids = []
        else:
            for id in id_list:
                self.graph.delete_figure(id)
            return []

    
    def draw_dice(self):
        self.die_faces = []
        for dice in range(self.number_of_dice):
            new_die_face = DieFace(graph=self.graph, images=self.f.images, stack_position=dice)
            self.die_faces.append(new_die_face)
        # roll info separator
        self.graph.draw_line((-40, 20), (-84, 20))

    
    def find_box_size(self):
        # should be a smooth function from 2px to x% of drawing area
        viewing_window_height = int(self.f.sim_viewing_height * 0.75)  
        highest_probability = float(max(self.convolution))
        print(f'{highest_probability = }', end=" : ")
        approx_most_outcomes = self.number_of_rolls * highest_probability * 1
        approx_most_outcomes = int(approx_most_outcomes) if approx_most_outcomes > 1 else 1
        print(f'{approx_most_outcomes = }')
        box_height = viewing_window_height // approx_most_outcomes
        worst_case_px_size = approx_most_outcomes * box_height
        print(f"{worst_case_px_size = }")
        if box_height < 2:
            box_height = 2
        if box_height > 0.10 * viewing_window_height:
            box_height = 0.075 * viewing_window_height
        box_width = self.top_right[0] // len(self.convolution)
        print(f'{box_width = }, {box_height = }')
        return box_width, box_height
    

    def make_partition(self, distribution=None):
        if distribution is None:
            distribution = self.dist
        partition = [0]
        total = 0
        for i in range(len(distribution)):
            total += distribution[i]
            partition.append(total)
        return partition
    
    
    def roll_dice(self, count:int = 1):
        counter = self.outcome_counter
        # b64_image_data = getattr(self.f.images, f'die{(count % 6) + 1}')
        # self.f.window['dice gif'].update(data=b64_image_data)
        if count == 1:
            prev_roll = None
        else:
            prev_roll = self.rolls[count - 2]  # - 2 since count starts at 1, but rolls index starts at 0
        this_roll = Roll(sim=self, roll_number=count, partition=self.partition, counter=counter, box_size=(self.box_width, self.box_height), 
                         graph=self.graph, dice=self.number_of_dice, previous_roll=prev_roll)
        self.rolls.append(this_roll)
        self.bin_dictionary[int(this_roll.sum)].append(this_roll)
        return this_roll


# ----------------------------------------------------------------------------------------------------------------------
# 8888888b.          888 888 
# 888   Y88b         888 888 
# 888    888         888 888 
# 888   d88P .d88b.  888 888 
# 8888888P" d88""88b 888 888 
# 888 T88b  888  888 888 888 
# 888  T88b Y88..88P 888 888 
# 888   T88b "Y88P"  888 888
#
# - A member of a simulation
# ----------------------------------------------------------------------------------------------------------------------
class Roll:
    def __init__(self, sim: Simulation, roll_number: int, partition, counter, box_size, graph, dice, previous_roll):
        # rolls all the dice and creates a Roll object according to the outcome
        # Inheritance
        self.sim: Simulation = sim
        self.roll_number: int = roll_number
        self.box_width: int | float = box_size[0]
        self.box_height: int | float = box_size[1]
        self.graph: sg.Graph = graph
        self.dice: int = dice  # number of dice to be thrown
        self.prev_roll: Roll = previous_roll

        # Rolling
        outcome: list = [0] * 6
        self.individual_outcomes: list = []
        for i in range(dice):
            roll = random.random()
            for j in range(7):
                if partition[j] <= roll < partition[j + 1]:
                    outcome[j] += 1
                    try:  # set the images and record the individual outcomes
                        if not self.sim.displaying_roll:
                            sim.die_faces[i].set_image(j + 1)
                        self.individual_outcomes.append(j + 1)
                    except TypeError as te:
                        print(f"index out of range, {i = }, {j + 1 = }\n{te}")
                        raise TypeError
        this_sum: int = np.dot(outcome, [1, 2, 3, 4, 5, 6])

        try:  # the roll landed in a displayed bin, create and draw the Roll
            counter[this_sum] += 1
            self.frequency = counter[this_sum]
            self.sum = this_sum  # X-coord in grid squares
            self.outcome = outcome

            # bottom left corner in pixels
            y_coord = (counter[this_sum] - 1) * self.box_height  
            x_coord = (this_sum - self.sim.possible_outcomes[0]) * self.box_width
            self.px_coord = (x_coord, y_coord)
            self.hitbox = self.make_hitbox()

            self.id: int
            self.draw_roll(*self.hitbox)
            if not self.sim.displaying_roll:
                self.display(set_faces=False)

        # TODO Outliers are not properly handled, the object still needs to be instantiated in some way
        # As it is, outliers are *very* rare but crash the program.
        except KeyError as ke:  
            print(f'{this_sum = }\n{counter = }\n\n{ke}')
            sg.popup_quick_message(f'Outlier encountered: {this_sum}', background_color='#1b1b1b', text_color='#fafafa', auto_close_duration=1, grab_anywhere=True, keep_on_top=True)


    def make_hitbox(self):
        # top-left, bottom-right
        top_left = (self.px_coord[0], self.px_coord[1] + self.box_height)
        bottom_right = self.px_coord[0] + self.box_width, self.px_coord[1]
        return top_left, bottom_right
    
    
    def draw_roll(self, t_l=None, b_r=None, fill='green'):
        if t_l is None:
            t_l = (0, self.box_height)
        if b_r is None:
            b_r = (self.box_width, 0)
        if self.prev_roll:  # change the previous roll to 'cyan' if its column isn't being highlighted. If it is, 'RoyalBlue' instead.
            previous_box_id = self.prev_roll.id
            box_color = 'Royal Blue' if self.prev_roll.sum == self.sim.selected_bin else 'cyan'
            self.graph.TKCanvas.itemconfig(previous_box_id, fill=box_color)
        self.id = self.graph.draw_rectangle(top_left=t_l, bottom_right=b_r, fill_color=fill)

    
    def is_hit(self, click: tuple, xoffset: int = 0, yoffset: int = 0, offset: None | int = None):
        if offset is not None:
            xoffset = offset
            yoffset = offset
        if click:
            half_length = abs(self.hitbox[0][0] - self.hitbox[1][0]) / 2
            half_height = abs(self.hitbox[0][1] - self.hitbox[1][1]) / 2
            center = (self.px_coord[0] + half_length, self.px_coord[1] + half_height)
            dx = abs(click[0] - center[0])
            dy = abs(click[1] - center[1])
            if dx - half_length <= xoffset and dy - half_height <= yoffset:
                return True
            else:
                return False
        else:
            return False
        
    
    def display(self, set_faces=True):
        if set_faces:
            for i, outcome in enumerate(self.individual_outcomes):
                self.sim.die_faces[i].set_image(outcome)
        self.sim.delete_ids()
        self.sim.display_ids.append(
            self.graph.draw_text(text=f"{self.frequency}",location=(-4 - (len(str(self.frequency))) * 6.33, self.px_coord[1] + self.box_height), 
                                 text_location=sg.TEXT_LOCATION_LEFT, color='magenta', font='_ 10 bold'))
        self.sim.display_ids.append(self.graph.draw_text(self.sum, location=(-62, 0), color='black', font='_ 16 bold'))
        self.sim.display_ids.append(self.graph.draw_text(text=f"Roll: {self.roll_number}", location=(-84, -40),
                                                         text_location=sg.TEXT_LOCATION_LEFT, color='magenta', font='_ 16 bold'))

        
    def __repr__(self) -> str:
        return f"Roll: {self.roll_number}\n  Outcome = {self.sum}, Occurrence = {self.frequency}  \n{' ' * 18}1  2  3  4  5  6\n  Dice Outcomes: {self.outcome}\n  {self.individual_outcomes = }"



# ----------------------------------------------------------------------------------------------------------------------
# 888888b.                    
# 888  "88b                   
# 888  .88P                   
# 8888888K.   8888b.  888d888 
# 888  "Y88b     "88b 888P"   
# 888    888 .d888888 888     
# 888   d88P 888  888 888     
# 8888888P"  "Y888888 888      
# 
# - A member of a convolution, uses the simulation when a bar is selected
# ----------------------------------------------------------------------------------------------------------------------
class Bar:
    def __init__(self, conv, bin, prob, size, coord):
        self.conv: Convolution = conv
        self.graph = self.conv.graph
        self.bin = bin                          # the label of the bin (not the index of the bin)
        self.probability = prob                 # probability of the sum
        self.size = size                        # pixel size of the bar
        self.x_coord = coord                    # x-coordinate of the bottom left corner
        self.hitbox = self.make_hitbox()        # (top-left, bottom-right)
        self.draw_bar(*self.hitbox)             # draws itself on the convolution graph


    def __repr__(self) -> str:
        return f"Sum = {self.bin}, probability = {self.probability}"
    
    
    def __eq__(self, other: Self) -> bool:
        return self.probability == other.probability and self.bin == other.bin
    
    
    def __lt__(self, other: Self) -> bool:
        return self.probability < other.probability and self.bin < other.bin
    
    
    def make_hitbox(self):
        top_left = (self.x_coord, self.size[1])
        bottom_right = (self.x_coord + self.size[0], 0)
        return top_left, bottom_right
    
           
    def draw_bar(self, t_l=None, b_r=None, fill='RoyalBlue4'):
        if t_l is None:  # top_left
            t_l = (0, self.size[1])
        if b_r is None:  # bottom_right
            b_r = (self.size[0], 0)
        self.graph.draw_rectangle(top_left=t_l, bottom_right=b_r, fill_color=fill)


    def is_hit(self, click: tuple, xoffset: int = 0, yoffset: int = 0, offset: None | int = None):
        if offset is not None:
            xoffset = offset
            yoffset = offset
        if click:
            half_length = abs(self.hitbox[0][0] - self.hitbox[1][0]) / 2
            half_height = abs(self.hitbox[0][1] - self.hitbox[1][1]) / 2
            center = (self.hitbox[0][0] + half_length, self.hitbox[1][1] + half_height)
            dx = abs(click[0] - center[0])
            dy = abs(click[1] - center[1])
            if dx - half_length <= xoffset and dy - half_height <= yoffset:
                return True
            else:
                return False
        else:
            return False
        
    
    def display(self):
        # delete any previous display on the convolution graph, then draw the display info.
        self.conv.current_selection = self.bin
        self.conv.delete_ids()  # default is these selection ids
        self.conv.selected_bar_display_ids.append(self.graph.draw_text(
                text=f"Sum: {self.bin}  |  p = {self.probability:.4f}", location=(8, self.conv.top_right[1] - 15), 
                color='magenta', font='_ 14 bold', text_location=sg.TEXT_LOCATION_LEFT
            )
        )
        expected_rolls = round(int(self.conv.f.values['rolls']) * self.probability)
        self.conv.selected_bar_display_ids.append(self.graph.draw_text(
                text=f"{expected_rolls} Expected Occurrences", location=(425, self.conv.top_right[1] - 12), 
                color='black', font='_ 12 bold', text_location=sg.TEXT_LOCATION_RIGHT
            )
        )
        
        # highlight all the rolls in the currently displaying bin, on the simulation
        if self.conv.f.sim:
            sim: Simulation = self.conv.f.sim  # this bar lives in a convolution, which is housed in a frame. the frame has a simulation.
            if self.conv.f.matching_graphs:
                previous_bin = sim.selected_bin
                sim.selected_bin = self.bin
                sim.select_bin(previous_bin)
                sim.draw_column_outlines(bin_number=self.bin - self.conv.possible_outcomes[0])
            else:
                sim.deselect_all_bins()
        return