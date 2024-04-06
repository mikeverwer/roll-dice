import matplotlib.ticker as ticker
import random
import PySimpleGUI as sg
import numpy as np

class mainframe:
    def __init__(self, images=None, window=None, values={}):
        print('[LOG] Initializing frame... ', end='')
        self.images = images
        self.window = window
        self.values = values
        self.locked_values = [0] * 6
        self.locks = [False] * 6
        self.preset_list = ['Fair', 'Sloped', 'Valley', 'Hill', 'Alternating']
        self.presets = {
               'Fair': [float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), 100 - float(500 / 6)],
               'Sloped': [47, 23, 16, 8, 4, 2],
               'Valley': [40, 8, 2, 3, 9, 38],
               'Hill': [2, 12, 40, 38, 7, 1],
               'Alternating': [32, 0, 32, 0, 32, 4],
        }
        self.die_distribution = self.random_distribution(get_var=True)
        print(f"Starting die distribution: {self.die_distribution}", end='... ')
        self.dice = 1
        self.mean, self.deviation = self.mean_and_deviation([value / 100 for value in self.die_distribution], update=False)
        self.update_interval = 64
        self.sim_margins: list[list[int]] = [[100, 75], [50, 50]]  #(left, right), (bottom, top)
        self.sim_graph_size = (996, 10000)
        self.con_margins: list[list[int]] = [[25, 25], [25, 10]]  #(left, right), (bottom, top)
        self.con_graph_size = (450, 325)
        self.con_graph = None
        self.extra_space = 0
        self.logging_UI_text = ' '
        self.simulate = False
        self.convolution = convolution(self)
        self.convolution_title = f' The Probability Distribution for the Sum of {self.dice} Dice '
        print(f'Complete!\n')
        

    def random_distribution(self, get_var=False):
        locked_sum = sum(self.locked_values)
        sum_to = 100 - locked_sum
        random_values = []
        for locked in self.locks:
            if not locked:
                random_values.append(random.random())
        total = sum(random_values)
        normalized_values = [int((sum_to * value) / total) for value in random_values]
        normalized_values[-1] = int(sum_to - sum(normalized_values[:-1]))
        valid_distribution = []
        lock_counter = 0
        unlock_counter = 0
        for locked in self.locks:
            if locked:
                valid_distribution.append(int(self.locked_values[lock_counter]))
            else:
                valid_distribution.append(normalized_values[unlock_counter])
                unlock_counter += 1
            lock_counter += 1

        if get_var:
            return valid_distribution
        else:
            self.die_distribution = valid_distribution


    def mean_and_deviation(self, distribution=None, update=True, dice: int = 1):
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
        mean += (dice - 1)
        
        if update:
            self.window['mean'].update(f'Mean: {mean:.2f}')
            self.window['deviation'].update(f'Standard Deviation: {standard_deviation:.2f}')
        if get_vars:
            return mean, standard_deviation
        else: self.mean, self.deviation = mean, standard_deviation

    
    def activate_hit_detect(self,click, graph: sg.Graph, event, objects: list[object], prev_selection: tuple[int, object] = (None, None)):
        selection_id = prev_selection[0]
        if selection_id:  # delete drawings 
            graph.delete_figure(selection_id)
        found = False
        print(f"Clicked {event}: {click}, \nLooking... ", end="")
        for Object in objects:
            if not found:
                if Object.is_hit(click):
                    found = True
                    Object.display=True
                    selection_id = graph.draw_rectangle(Object.hitbox[0], Object.hitbox[1], 'magenta')
                    print(f'found {Object}')
                    return selection_id, Object
        if not found:
            print('Found nothing.')


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
        for i in range(1, 7):  # Update sliders and locks
            if self.locks[i - 1] and reset_locks is True:  # Reset locks
                self.locks[i - 1] = False
                b64_image_data = getattr(self.images, f'die{i}')
                self.window[f'lock{i}'].update(image_data=b64_image_data)
            self.values[f'face{i}'] = slider_values[i - 1]
            self.window[f'face{i}'].update(self.values[f'face{i}'])

        self.die_distribution = slider_values
        self.mean_and_deviation(slider_values)
        self.convolution = convolution(self)


    def activate_slider(self, event, active_face=None, set_to_value=None):
        if set_to_value is None:
            set_to_value = self.values[event]
        if active_face is None:
            active_face = int(event[-1])
        self.values[event] = set_to_value

        # If the face is not locked, accept and adjust other faces
        if not self.locks[active_face - 1]:  
            active_slider_key = event
            active_slider_value = self.values[event]
            slider_values = [self.values[f'face{i}'] for i in range(1, 7)]
            total = sum(slider_values)
            locked_sum = sum(self.locked_values)
            unlocked_sum = total - active_slider_value - locked_sum

            # Scale the other sliders
            if total != 100 and unlocked_sum != 0:  # scaling is required and there is at least 1 locked slider
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
  
            # The unlocked sliders were all 0 and the active slider was reduced; increase an unlocked slider
            elif unlocked_sum == 0 and total < 100:
                next_unlocked_face = None
                for i in range(1, 6):
                    # Find an unlocked slider. If there are none, lock the active slider
                    next_face = ((active_face - 1) + i) % 6
                    if self.locks[next_face]:  # Skip locked sliders
                        next_unlocked_face = None
                        continue
                    else:
                        next_unlocked_face = next_face + 1
                        break
                
                # No unlocked faces were found; lock active face
                if next_unlocked_face is None: 
                    adjustment = 100 - total
                    slider_values[active_face - 1] += adjustment
                    self.window[active_slider_key].update(slider_values[active_face - 1])
                # Found a slider to adjust
                else:
                    self.values[f'face{next_unlocked_face}'] = 100 - active_slider_value
                    self.window[f'face{next_unlocked_face}'].update(self.values[f'face{next_unlocked_face}'])

            # The unlocked sliders were all 0 and the active slider was increased; decrease active slider
            elif unlocked_sum == 0 and total > 100:
                adjustment = 100 - total
                slider_values[active_face - 1] += adjustment
                self.window[active_slider_key].update(slider_values[active_face - 1])

            # Finished moving, update related objects
            self.mean_and_deviation(slider_values)
            self.die_distribution = [_ for _ in slider_values]
            self.convolution = convolution(self)

        else:  # Slider is locked, keep value constant
            self.values[event] = self.locked_values[int(event[-1]) - 1]
            self.window[event].update(self.values[event])


    def dice_change(self, value=None):
        if value is None:
            value = self.dice
        self.dice = value if value > 0 else 1
        self.window['dice'].update(value=self.dice)
        self.window['dist tab'].update(title=f' The Probability Distribution for the Sum of {self.dice} Dice ')
        self.convolution = convolution(self)


class convolution:
    def __init__(self, frame: mainframe):
        if frame.con_graph is None:
            print('Making Convolution', end='... ')
        self.f = frame
        self.bins: list[bar] = []
        self.die_dist = frame.die_distribution
        self.graph = frame.con_graph
        if sum(self.die_dist) != 1:
            self.die_dist = [x / sum(self.die_dist) for x in self.die_dist]
        else:
            self.die_dist = self.die_dist
        self.number_of_dice = self.f.dice
        # all possible outcomes
        self.possible_outcomes = list(range(self.number_of_dice, (6 * self.number_of_dice) + 1))
        self.conv_dist = self.create_convoluted_distribution(get_var=True)
        self.mean, self.deviation = self.f.mean_and_deviation(self.conv_dist, update=False, dice=self.number_of_dice)
        self.leftmost_bin: int = None
        self.rightmost_bin: int = None
        self.bin_width = 1
        self.scalar = 1
        if self.graph:
            self.make_bars()
        self.selection_box_id = None

    def create_convoluted_distribution(self, dice=None, get_var=False):
        if dice is None:
            dice = int(self.number_of_dice)
        convoluted_distribution = self.die_dist
        for _ in range(dice - 1):
            convoluted_distribution = np.convolve(convoluted_distribution, self.die_dist)
        # all possible outcomes
        outcomes = list(range(dice, 6 * dice))
        if get_var:
            return convoluted_distribution
        else: 
            self.conv_dist = convoluted_distribution

    def trim_outcomes(self):
        feasible_outcomes = self.possible_outcomes
        distribution = self.conv_dist
        number_of_bins = len(distribution)
        
        # feasible outcomes, within 3.5 st. dev.'s from the mean
        # outcomes = list(range(int(mean - (3.5 * deviation)), int(mean + (3.5 * deviation))))  

        # Check: values in distribution[int(mean - (5.5 * deviation))] and distribution[int(mean + (5.5 * deviation))] ~ 0?
        #        Need to handle boundary checking.
        # Trim outcomes and distribution accordingly

        left_border_index = int(self.mean - (5.5 * self.deviation))
        left_border_index = 0 if left_border_index < 0 else left_border_index
        right_border_index = int(self.mean + (5.5 * self.deviation))
        right_border_index = len(feasible_outcomes) - 1 if right_border_index >= len(feasible_outcomes) else right_border_index
        tol = 1
        left_bin_height = distribution[left_border_index] * self.scalar
        right_bin_height = distribution[right_border_index]
        
        for i, x in enumerate(distribution):
            found = False
            if not found:
                if x * self.scalar > 1:
                    left_border_index = i
                    found = True
        
        for i, x in enumerate(reversed(distribution)):
            found = False
            if not found:
                if x * self.scalar > 1:
                    right_border_index = len(distribution) - i
                    found = True
                    
        print(f"{left_border_index = }, {right_border_index = }")
        
        # if left_bin_height < tol and distribution[right_border_index] > tol:
        #     distribution = distribution[left_border_index:]
        #     feasible_outcomes = feasible_outcomes[left_border_index:]
        # elif distribution[left_border_index] > tol and distribution[right_border_index] < tol and right_border_index < len(feasible_outcomes) - 1:
        #     distribution = distribution[:right_border_index]
        #     feasible_outcomes = feasible_outcomes[:right_border_index]
        #     print('trimming RIGHT border only')
        #     print('new outcomes:')
        #     print(f"{len(feasible_outcomes) = }, {feasible_outcomes[0] = }, {feasible_outcomes[-1] = }\n")
        # elif distribution[left_border_index] < tol and distribution[right_border_index] < tol:
        #     distribution = distribution[left_border_index:right_border_index]
        #     feasible_outcomes = feasible_outcomes[left_border_index:right_border_index]
        #     print('trimming BOTH borders')
        #     print('new outcomes:')
        #     print(f"{len(feasible_outcomes) = }, {feasible_outcomes[0] = }, {feasible_outcomes[-1] = }\n")
        # else:
        #     print('No trim needed')
        
        feasible_outcomes = feasible_outcomes[left_border_index : right_border_index]
        self.possible_outcomes = feasible_outcomes
        distribution = distribution[left_border_index : right_border_index]
        self.conv_dist = distribution
        return
 
    
    def find_sizes(self):
        highest_probability = max(self.conv_dist)
        highest_point = self.top_right[1] * 0.75
        self.scalar = highest_point / highest_probability
        print('about to trim')
        # self.trim_outcomes()
        bins = len(self.conv_dist)
        self.bin_width = self.top_right[0] // bins
    
    def make_bars(self):
        self.graph.erase()
        self.bins: list[bar] = []
        self.graph = self.f.con_graph
        self.top_right = (self.f.con_graph_size[0] - sum(self.f.con_margins[0]), self.f.con_graph_size[1] - sum(self.f.con_margins[1]))
        self.graph.draw_rectangle((0, 0), self.top_right)
        # find grid points
        print('this runs')
        self.find_sizes()
        for i, x in enumerate(self.conv_dist):
            probability = x
            height = x * self.scalar
            x_location = i * self.bin_width
            bin_number = i + self.number_of_dice
            new_bar = bar(graph=self.graph, bin=bin_number, prob=probability, size=(self.bin_width, height), coord=x_location)
            self.bins.append(new_bar)

    def display(self):
        pass


class bar:
    def __init__(self, graph, bin, prob, size, coord):
        self.graph = graph
        self.bin = bin
        self.probability = prob
        self.size = size
        self.x_coord = coord
        self.hitbox = self.make_hitbox()  # (top-left, bottom-right)
        self.display = False
        self.draw_bar(*self.hitbox)

    def __repr__(self) -> str:
        return f"Sum = {self.bin}\n"
    
    def make_hitbox(self):
        top_left = (self.x_coord, self.size[1])
        bottom_right = (self.x_coord + self.size[0], 0)
        return top_left, bottom_right
    
        
    def draw_bar(self, t_l=None, b_r=None, fill='RoyalBlue4'):
        if t_l is None:
            t_l = (0, self.size[1])
        if b_r is None:
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
        return



class simulation:
    def __init__(self, frame: mainframe):
        print('Beginning the simulation, enjoy!')
        # inheritance
        try:
            self.f: mainframe = frame
            self.graph: sg.Graph = self.f.window['simulation graph']
            self.dist: list[float] = [x / 100 for x in self.f.die_distribution]
            self.number_of_rolls: int = int(self.f.values['rolls'])
            self.number_of_dice: int = int(self.f.values['dice'])
            if self.number_of_dice < 1 or self.number_of_rolls < 1:
                raise Exception
        except:
            print("Cancelling... Could not gather the required inputs.")
            try:
                if self.number_of_dice < 1 or self.number_of_rolls < 1:
                    print('this ran from the except block')
                    raise ValueError("We must roll at least once.\nPlease enter a non-zero value.")
            except:
                raise ValueError("Please enter integers into the input fields.")
        # Self
        # self.f.window['log'].update(value='')
        self.f.window['sim column'].Widget.canvas.yview_moveto(1.0)
        self.selection_box_id = None
        self.partition = self.make_partition()
        self.possible_outcomes = list(range(self.number_of_dice, (6 * self.number_of_dice) + 1))
        self.outcome_counter: dict[int: int] = {}
        self.rolls: list[roll] = []
        self.convolution: list[float] = self.f.convolution.conv_dist       
        self.outcome_counter = {outcome: 0 for outcome in self.possible_outcomes}
        # Drawing area from (0, 0) to (x - 125 - 100, y - 50 - 50)
        # Current Drawing Area, (x, y) = (1000, 400) ==> (0, 0) to (775, 300)

        self.top_right = (self.f.sim_graph_size[0] - sum(self.f.sim_margins[0]), self.f.sim_graph_size[1] - sum(self.f.sim_margins[1]))
        self.box_width, self.box_height = self.find_box_size()
        self.drawing_area()
        self.trial_number = 1

    def drawing_area(self):
        self.graph.draw_rectangle((0,0), self.top_right)
        # Draw y-axis tick marks, labels, and grid lines
        y_tick_diff = self.number_of_rolls // 15 
        y_tick_diff = round(y_tick_diff / 5) * 5 if self.number_of_rolls > 44 else 5  # closest multiple of 5 to one tenth of the max rolls
        delta_y = y_tick_diff * self.box_height  # height difference in pixels
        y_tick_height = 0
        y_tick = 0
        while y_tick_height < self.top_right[1]:
            string_length = len(str(self.number_of_rolls)) if self.number_of_rolls > 100 else 3
            tick_string = f'{y_tick:>{string_length}}'
            self.graph.draw_line((-8, y_tick_height), (0, y_tick_height))
            self.graph.draw_line((0, y_tick_height), (self.top_right[0], y_tick_height), color='#dcdcdc')
            self.graph.draw_text(tick_string, location=(-(len(tick_string) * 6.33) , y_tick_height)) 
            y_tick_height += delta_y
            y_tick += y_tick_diff
        # Draw x-axis tick marks and labels
        box_center = self.box_width / 2
        x_tick_diff = np.gcd(6, (self.possible_outcomes[-1] - self.possible_outcomes[0]))
        x_tick_diff = len(self.possible_outcomes) // 6
        print(f"{x_tick_diff = }")
        # locator = ticker.AutoLocator()
        # locator.axis.set_view_interval((self.possible_outcomes[0], self.possible_outcomes[-1]))
        # xtick_positions = locator()
        # xtick_intervals = [xtick_positions[i + 1] - xtick_positions[i] for i in range(len(xtick_positions)-1)]
   
        # x_tick_diff = (self.possible_outcomes[-1] - self.possible_outcomes[0] + 1) // 6
        for i, bin in enumerate(self.possible_outcomes):
            self.graph.draw_line(((i * self.box_width) + box_center, -1), ((i * self.box_width) + box_center, -10))
            if i % x_tick_diff == 0:
            # if i in xtick_intervals:
                self.graph.draw_text(f'{bin}', location=((i * self.box_width) + box_center, -15))



    
    def find_box_size(self):
        # should be a smooth function from 3px to x% of drawing area
        drawing_window_height = 630
        highest_probability = float(max(self.convolution))
        print(f'{highest_probability = }', end=" : ")
        approx_most_outcomes = self.number_of_rolls * highest_probability * 1.5
        approx_most_outcomes = int(approx_most_outcomes) if approx_most_outcomes > 1 else 1
        print(f'{approx_most_outcomes = }')
        box_height = drawing_window_height // approx_most_outcomes
        worst_case = approx_most_outcomes * box_height
        print(f"{worst_case = }")
        if box_height < 2:
            box_height = 2
        if box_height > 0.10 * drawing_window_height:
            box_height = 0.08 * drawing_window_height
        box_width = self.top_right[0] // len(self.convolution)
        print(f'{box_width = }, {box_height = }')
        return box_width, box_height
 
    def draw_axis(self):
        ticks = None

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
        box_size = (self.box_width, self.box_height)
        graph = self.graph
        if count == 1:
            prev_roll = None
        else:
            prev_roll = self.rolls[count - 2]  # - 2 since count starts at 1, but rolls index starts at 0
        this_roll = roll(self, roll_number=count, partition=self.partition, counter=counter, box_size=box_size, 
                         graph=graph, dice=self.number_of_dice, previous_roll=prev_roll)
        self.rolls.append(this_roll)
        print(this_roll.outcome)
        return this_roll


class roll:
    def __init__(self, sim: simulation, roll_number: int, partition, counter, box_size, graph, dice, previous_roll):
        self.sim = sim
        self.roll_number = roll_number
        self.box_width = box_size[0]
        self.box_height = box_size[1]
        self.graph = graph
        self.dice = dice
        self.prev_roll = previous_roll

        outcome = [0] * 6
        for _ in range(dice):
            roll = random.random()
            for j in range(7):
                if partition[j] <= roll < partition[j + 1]:
                    outcome[j] += 1
        this_sum = np.dot(outcome, [1, 2, 3, 4, 5, 6])

        try:
            counter[this_sum] += 1
        except KeyError as ke:
            print(f'{this_sum = }\n{counter = }\n\n{ke}')

        try:
            self.frequency = counter[this_sum]
        except KeyError as ke:
            print(f'{this_sum = }\n{counter = }\n\n{ke}')

        # bottom left corner in pixels
        y_coord = (counter[this_sum] - 1) * self.box_height  
        x_coord = (this_sum - dice) * self.box_width
        self.outcome = outcome
        self.sum = this_sum  # X-coord in grid squares
        self.px_coord = (x_coord, y_coord)
        self.grid_coord = (self.sum - dice, self.frequency - 1)
        self.hitbox = self.make_hitbox()
        self.id: int 
        self.draw_roll(*self.hitbox)
        self.display = self.is_hit(click=None)
        
    def __repr__(self) -> str:
        return f""
    

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
        if self.prev_roll:
            previous_box_id = self.prev_roll.id
            self.graph.TKCanvas.itemconfig(previous_box_id, fill='cyan')
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
