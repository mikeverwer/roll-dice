import random
from typing import Self
import PySimpleGUI as sg
import numpy as np

"""
The classes required for the Roll Dice simulation window.  The utilization of the classes is described below.

A `Mainframe` houses the window sg object and the values dictionary, the convolution of the `n` die, as well as 
the simulation of the rolls.

A `Convolution` is an object that has a convoluted distribution graph with each of the bars of the graph being
their own individual `Bar` objects.  This is the theoretical probability distribution for rolling the `n` dice.

The `Simulation` class controls the entire simulation. It is invoked as an object by the `EventHandler` and the step is 
incremented there.  The simulation creates `Roll` objects and draws them on the graph.  
Each `Roll` is remembered by the `simulation` and, when selected, will display the outcome of each die rolled.

Note: A `simulation` requires a `mainframe` as an initializing variable, so it can only be created AFTER the
    mainframe has been fully instantiated. Whereas the `mainframe` instantiates its own `convolution`.  

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
# - Not Implemented.
# ----------------------------------------------------------------------------------------------------------------------
class EventHandler:
    def __init__(self, frame) -> None:
        self.mf = frame

    def handle(self, event) -> None:
        mf = self.mf
        # the code from inside the event loop goes here.


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
class Mainframe:
    def __init__(self, images=None, window=None, values={}):
        print('[LOG] Initializing frame... ', end='')
        # Inheritance
        self.images = images
        self.window = window
        self.values = values
        
        # Self
        # Initializing frame variables
        self.preset_list = ['Fair', 'Sloped', 'Valley', 'Hill', 'Alternating']
        self.presets = {
               'Fair': [float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), 100 - float(500 / 6)],
               'Sloped': [47, 23, 16, 8, 4, 2],
               'Valley': [40, 8, 2, 3, 9, 38],
               'Hill': [2, 12, 40, 38, 7, 1],
               'Alternating': [32, 0, 32, 0, 32, 4],
        }
        self.dice = 1  # number of dice

        # Controlling variables
        self.update_interval = 64       # controls framerate / speed of simulation
        self.simulate = False           # turns the simulation on or off (pause/play)
        self.matching_graphs = False    # if the graphs match, we can select and compare columns between sim. and conv.

        # Graph dimensions and margins
        # Simulation graph
        self.sim_margins: list[list[int]] = [[100, 20], [75, 50]]  # (left, right), (bottom, top)
        self.sim_graph_size: tuple[int, int] = (1000, 10000)       # the height extends far past what is shown to allow for many rolls, the values get overridden in make_window
        self.sim_viewing_height: int = None                        # height of the simulation graph that gets displayed
        self.sim_graph: sg.Graph = None
        # Convolution graph
        self.con_margins: list[list[int]] = [[10, 10], [25, 10]]   # (left, right), (bottom, top)
        self.con_graph_size: tuple[int, int] = (450, 325)
        self.con_graph: sg.Graph = None

        # Single Die Distribution
        self.locked_values: list[int] = [0] * 6     # List to hold the values that each slider may be locked at.
        self.locks: list[bool] = [False] * 6        # List of bools to keep track of which sliders are locked 
        self.die_distribution: list[float | int] = self.random_distribution(get_var=True)  # distribution that sums to 100
        print(f"Starting die distribution: {self.die_distribution}", end='... ')
        self.mean, self.deviation = self.mean_and_deviation([value / 100 for value in self.die_distribution], update=False)  # Type: float, float
        
        # Initialize Simulation 
        self.sim: Simulation = None

        # Initialize Convolution
        self.convolution_title = f' The Probability Distribution for the Sum of {self.dice} Dice '
        self.convolution: Convolution = Convolution(self)  # requires a frame as a parameter
        self.convolution_display_ids = []                  # Figure ID's for the figures of the bar display method on the convolution graph

        print(f'Complete!\n')

    
    def resize_graphs(self):
        """
        The graphs do not actually get resized.  When initialized, the graph has a width and view height that fill the available screen size. 
        This function re-defines the drawing area of the simulation to fit in the new window size.
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

        elif click[0] > 0 and click[1] > 0:  # only search for objects if the click is in the graphing region
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
        x_tick_label_diff = len(self.possible_outcomes) // 5  # ensures there are always 6 tick labels
        for i, bin in enumerate(self.possible_outcomes):
            box_center = self.bin_width * (i + 0.5)
            self.graph.draw_line((box_center, -1), (box_center, -5))   # box_center = self.box_width * (i + 0.5)
            if i % x_tick_label_diff == 0:
                self.graph.draw_text(f'{bin}', location=(box_center, -10))
 
    
    def find_sizes(self):
        highest_probability = max(self.conv_dist)
        self.highest_point = self.top_right[1] - 45
        self.scalar = self.highest_point / highest_probability
        if self.number_of_dice > 4:
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
        expected_rolls = int(int(self.conv.f.values['rolls']) * self.probability)
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