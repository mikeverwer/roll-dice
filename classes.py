import random
import numpy as np

class mainframe:
    def __init__(self, images=None, window=None, values={}):
        print('[LOG] initializing frame... ', end='')
        self.images = images
        self.window = window
        self.values = values
        self.locked_values = [0] * 6
        self.locks = [False] * 6
        self.preset_list = ['Fair', 'Sloped', 'Valley', 'Hill']
        self.presets = {
               'Fair': [float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), float(100 / 6), 100 - float(500 / 6)],
               'Sloped': [47, 23, 16, 8, 4, 2],
               'Valley': [40, 8, 2, 3, 9, 38],
               'Hill': [2, 12, 40, 38, 7, 1]
        }
        self.die_distribution = self.random_distribution(get_var=True)
        self.dice = 3
        self.mean, self.deviation = self.mean_and_deviation([value / 100 for value in self.die_distribution], update=False)
        self.update_interval = 64
        self.sim_margins: list[list[int]] = [[150, 75], [50, 50]]  #(left, right), (bottom, top)
        self.sim_graph_size = (1000, 800)
        self.con_margins: list[list[int]] = [[25, 25], [25, 10]]  #(left, right), (bottom, top)
        self.con_graph_size = (450, 300)
        self.con_graph = None
        self.extra_space = 0
        self.logging_UI_text = ' '
        self.simulate = False
        self.convolution = convolution(self)
        self.convoluted_distribution = self.create_convoluted_distribution(self.dice, get_var=True)
        print(f'Complete!\nStarting die distribution: {self.die_distribution}')
        

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

    
    def create_convoluted_distribution(self, dice=None, get_var=False, draw=False):
        if dice is None:
            dice = int(self.values['dice'])
        if sum(self.die_distribution) != 1:
            static_dist = [x / 100 for x in self.die_distribution]
        else:
            static_dist = self.die_distribution
        convoluted_distribution = static_dist
        for _ in range(dice - 1):
            convoluted_distribution = np.convolve(convoluted_distribution, static_dist)
        # all possible outcomes
        outcomes = list(range(dice, 6 * dice))
        if get_var:
            return convoluted_distribution
        else: 
            self.convoluted_distribution = convoluted_distribution
        if draw:
            self.draw_convoluted_distribution(convoluted_distribution)

    def draw_convoluted_distribution(self, dist=None):
        if dist is None:
            dist = self.convoluted_distribution


    def add_preset(self, new_preset: str):
        self.preset_list.append(new_preset)
        self.presets[new_preset] = self.die_distribution
        self.window['preset'].update(values=self.preset_list)
        print(f"[LOG] New Preset added.\n{new_preset} : {self.presets[new_preset]}")

    
    def activate_lock(self, active_lock):
        self.locked_values[active_lock - 1] = self.values[f'face{active_lock}']
        self.locks[active_lock - 1] = not self.locks[active_lock - 1]
        if self.locks[active_lock - 1]:
            self.window[f'lock{active_lock}'].update(image_data=self.images[f'lock{active_lock}'])
        else:
            self.window[f'lock{active_lock}'].update(image_data=self.images[f'die{active_lock}'])
            self.locked_values[active_lock - 1] = 0


    def set_sliders_to(self, slider_values, reset_locks=False):
        for i in range(1, 7):  # Update sliders and locks
            if self.locks[i - 1] and reset_locks is True:  # Reset locks
                self.locks[i - 1] = False
                self.window[f'lock{i}'].update(image_data=self.images[f'die{i}'])
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

            #  The unlocked sliders were all 0 and the active slider was increased; decrease active slider
            elif unlocked_sum == 0 and total > 100:
                adjustment = 100 - total
                slider_values[active_face - 1] += adjustment
                self.window[active_slider_key].update(slider_values[active_face - 1])

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
        self.convolution = convolution(self)

class convolution:
    def __init__(self, frame: mainframe):
        print('Making Convolution')
        self.f = frame
        self.bins: list[bar] = []
        self.die_dist = frame.die_distribution
        self.graph = frame.con_graph
        if sum(self.die_dist) != 1:
            self.die_dist = [x / 100 for x in self.die_dist]
        else:
            self.die_dist = self.die_distribution
        self.number_of_dice = self.f.dice
        # all possible outcomes
        self.possible_outcomes = list(range(self.number_of_dice - 1, (6 * self.number_of_dice) + 1))
        self.conv_dist = self.create_convoluted_distribution(get_var=True)
        self.trim_outcomes()
        self.bin_width = 1
        self.scalar = 1
        if self.graph:
            self.make_bars()

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
        # feasible outcomes, within 3.5 st. dev.'s from the mean
        # outcomes = list(range(int(mean - (3.5 * deviation)), int(mean + (3.5 * deviation))))  

        # Check: values in distribution[int(mean - (5.5 * deviation))] and distribution[int(mean + (5.5 * deviation))] ~ 0?
        #        Need to handle boundary checking.
        # Trim outcomes and distribution accordingly

        # left_border_index = int(mean - (5.5 * deviation))
        # print(f'{left_border_index = }')
        # left_border_index = 0 if left_border_index < 0 else left_border_index
        # right_border_index = int(mean + (5.5 * deviation))
        # print(f'{right_border_index = }')
        # right_border_index = len(outcomes) - 1 if right_border_index > len(outcomes) - 1 else right_border_index
        # tol = 1e-4
        # print(f"{left_border_index = }, {right_border_index = }")
        # print(f"  y at {left_border_index} = {distribution[left_border_index]},\n  y at {right_border_index} = {distribution[right_border_index]}")
        # print('original outcomes:')
        # print(f"{len(outcomes) = }, {outcomes[0] = }, {outcomes[-1] = }")
        # if distribution[left_border_index] < tol and distribution[right_border_index] > tol and left_border_index > 0:
        #     distribution = distribution[left_border_index:]
        #     outcomes = outcomes[left_border_index:]
        #     print('trimming LEFT border only')
        #     print('new outcomes:')
        #     print(f"{len(outcomes) = }, {outcomes[0] = }, {outcomes[-1] = }\n")
        # elif distribution[left_border_index] > tol and distribution[right_border_index] < tol and right_border_index < len(outcomes) - 1:
        #     distribution = distribution[:right_border_index]
        #     outcomes = outcomes[:right_border_index]
        #     print('trimming RIGHT border only')
        #     print('new outcomes:')
        #     print(f"{len(outcomes) = }, {outcomes[0] = }, {outcomes[-1] = }\n")
        # elif distribution[left_border_index] < tol and distribution[right_border_index] < tol:
        #     distribution = distribution[left_border_index:right_border_index]
        #     outcomes = outcomes[left_border_index:right_border_index]
        #     print('trimming BOTH borders')
        #     print('new outcomes:')
        #     print(f"{len(outcomes) = }, {outcomes[0] = }, {outcomes[-1] = }\n")
        # else:
        #     print('No trim needed')
        return feasible_outcomes
 
    
    def find_sizes(self):
        bins = len(self.conv_dist)
        self.bin_width = self.top_right[0] // bins
        highest_probability = max(self.conv_dist)
        highest_point = self.top_right[1] * 0.9
        self.scalar = highest_point / highest_probability
    
    def make_bars(self):
        self.graph.erase()
        self.bins: list[bar] = []
        self.graph = self.f.con_graph
        self.top_right = (self.f.con_graph_size[0] - sum(self.f.con_margins[0]), self.f.con_graph_size[1] - sum(self.f.con_margins[1]))
        self.graph.draw_rectangle((0, 0), self.top_right)
        # find grid points
        self.find_sizes()
        for i, x in enumerate(self.conv_dist):
            height = x * self.scalar
            x_location = i * self.bin_width
            bin_number = i + self.number_of_dice
            new_bar = bar(graph=self.graph, bin=bin_number, size=(self.bin_width, height), coord=x_location)
            self.bins.append(new_bar)


class bar:
    def __init__(self, graph, bin, size, coord):
        self.graph = graph
        self.bin = bin
        self.size = size
        self.x_coord = coord
        self.hitbox = self.make_hitbox()  # (top-left, bottom-right)
        self.display = False
        self.draw_bar(*self.hitbox)
    
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



class simulation:
    def __init__(self, frame: mainframe):
        print('Beginning the simulation, enjoy!')
        # inheritance
        self.f = frame
        self.graph = self.f.window['simulation graph']
        self.dist = [x / 100 for x in self.f.die_distribution]
        self.number_of_rolls = int(self.f.values['rolls'])
        self.number_of_dice = int(self.f.values['dice'])
        # child
        # self.f.window['log'].update(value='')
        self.partition = self.make_partition()
        self.possible_outcomes = list(range(self.number_of_dice - 1, (6 * self.number_of_dice) + 1))
        self.outcome_counter: dict[int: int] = {}
        self.rolls: list[roll] = []
        self.convolution = self.f.convolution.conv_dist       
        self.outcome_counter = {outcome: 0 for outcome in self.possible_outcomes}
        # Drawing area from (0, 0) to (x - 125 - 100, y - 50 - 50)
        # Current Drawing Area, (x, y) = (1000, 400) ==> (0, 0) to (775, 300)

        self.top_right = (self.f.sim_graph_size[0] - sum(self.f.sim_margins[0]), self.f.sim_graph_size[1] - sum(self.f.sim_margins[1]))
        self.drawing_area = self.graph.draw_rectangle((0,0), self.top_right)
        self.box_width, self.box_height = self.find_box_size()
        self.trial_number = 1
    
    def find_box_size(self):
        # should be a smooth function from 3px to x% of drawing area
        highest_probability = float(max(self.convolution))
        print(f'{highest_probability = }', end=" : ")
        approx_most_outcomes = self.number_of_rolls * highest_probability * 1.5
        approx_most_outcomes = int(approx_most_outcomes)
        print(f'{approx_most_outcomes = }')
        box_height = self.top_right[1] // approx_most_outcomes
        worst_case = approx_most_outcomes * box_height
        print(f"{worst_case = }")
        if box_height < 2:
            box_height = 2
        if box_height > 0.10 * self.top_right[1]:
            box_height = 0.08 * self.top_right[1]
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
