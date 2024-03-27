import random

class frame:
    def __init__(self, window=None, values={}):
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
        self.die_distribution = self.random_distribution(get=True)
        self.mean, self.deviation = self.mean_and_deviation([value / 100 for value in self.die_distribution], get=True, update=False)
        self.dice = 3
        self.extra_space = 0
        self.logging_UI_text = ' '
        
    def random_distribution(self, get=False):
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

        self.die_distribution = valid_distribution
        if get:
            return self.die_distribution

    def mean_and_deviation(self, distribution, update=True, get=False):
        if abs(sum(distribution) - 100) <= 5:
            # Convert a distribution given in percentages to decimal
            valid_distribution = [item / 100 for item in distribution]
            valid_distribution[-1] = 1 - sum(valid_distribution[:-1])
            distribution = valid_distribution
        mean = 0
        for x in range(6):
            mean += (x + 1) * distribution[x]
        variance = 0
        for x in range(1, 7):
            variance += distribution[x - 1] * ((x - mean) ** 2)
        standard_deviation = variance ** .5
        if update:
            self.mean, self.deviation = mean, standard_deviation
            self.window['mean'].update(f'Mean: {mean:.2f}')
            self.window['deviation'].update(f'Standard Deviation: {standard_deviation:.2f}')
        if get is True:
            return mean, standard_deviation    

    def add_preset(self, new_preset: str):
        self.preset_list.append(new_preset)
        self.presets[new_preset] = self.die_distribution
        self.window['preset'].update(values=self.preset_list)

    def set_sliders_to(slider_values, reset_locks=False):
        for i in range(1, 7):  # Update sliders and locks
            if self.locks[i - 1] and reset_locks is True:  # Reset locks
                self.locks[i - 1] ^= True
                window[f'lock{i}'].update(image_filename=f'assets/die{active_lock}.png')
            values[f'face{i}'] = slider_values[i - 1]
            window[f'face{i}'].update(values[f'face{i}'])

        mean_and_deviation(slider_values)

'''
    # ----------------------------------------------------------------------------------------------------------------------
    # Functions
    # ----------------------------------------------------------------------------------------------------------------------

    def mean_and_deviation(distribution, update=True, get=False):
        if abs(sum(distribution) - 100) <= 5:
            # Convert a distribution given in percentages to decimal
            valid_distribution = [item / 100 for item in distribution]
            valid_distribution[-1] = 1 - sum(valid_distribution[:-1])
            distribution = valid_distribution

        mean = 0
        for x in range(6):
            mean += (x + 1) * distribution[x]
        variance = 0
        for x in range(1, 7):
            variance += distribution[x - 1] * ((x - mean) ** 2)
        standard_deviation = variance ** .5
        if update:
            values['mean'], values['deviation'] = mean, standard_deviation
            window['mean'].update(f'Mean: {mean:.2f}')
            window['deviation'].update(f'Standard Deviation: {standard_deviation:.2f}')
        if get is True:
            return mean, standard_deviation

    def set_sliders_to(slider_values, reset_locks=False):
        for i in range(1, 7):  # Update sliders and locks
            if self.locks[i - 1] and reset_locks is True:  # Reset locks
                self.locks[i - 1] ^= True
                window[f'lock{i}'].update(image_filename=f'assets/die{active_lock}.png')
            values[f'face{i}'] = slider_values[i - 1]
            window[f'face{i}'].update(values[f'face{i}'])

        mean_and_deviation(slider_values)

    def activate_slider(event, values, set_to_value=None):
        if set_to_value is None:
            set_to_value = values[event]
        active_face = int(event[-1])
        values[event] = set_to_value

        if not self.locks[active_face - 1]:  # If the face is not locked, accept and adjust other faces
            active_slider_key = event
            active_slider_value = values[event]
            slider_values = [values[f'face{i}'] for i in range(1, 7)]
            total = sum(slider_values)
            locked_sum = 0
            for i in range(1, 7):
                if self.locks[i - 1]:
                    locked_sum += values[f'face{i}']
            unlocked_sum = total - active_slider_value - locked_sum

            if total != 100 and unlocked_sum != 0:
                # Calculate the scaling factor to preserve the relative positions
                scaling_factor = (100 - active_slider_value - locked_sum) / unlocked_sum

                # Scale all sliders while preserving relative positions
                for i in range(1, 7):
                    if active_slider_key == f'face{i}' or self.locks[i - 1]:
                        # Skip the actively modified or locked slider
                        continue
                    else:
                        slider_values[i - 1] = int(slider_values[i - 1] * scaling_factor)
                        window[f'face{i}'].update(slider_values[i - 1])

                # Adjust active slider to ensure the sum is 100
                total = sum(slider_values)
                if total != 100 and total != 0:
                    adjustment = 100 - total
                    slider_values[active_face - 1] += adjustment
                    window[active_slider_key].update(slider_values[active_face - 1])

            elif unlocked_sum == 0 and total < 100:
                next_unlocked_face = None
                # The unlocked sliders were all 0 and the active slider was reduced; increase an unlocked slider
                for i in range(1, 6):
                    # Find an unlocked slider. If there are none, lock the active slider
                    next_face = ((active_face - 1) + i) % 6
                    if self.locks[next_face]:  # Skip locked sliders
                        next_unlocked_face = None
                        continue
                    else:
                        next_unlocked_face = next_face + 1
                        break

                if next_unlocked_face is None:  # No unlocked faces were found; lock active face
                    adjustment = 100 - total
                    slider_values[active_face - 1] += adjustment
                    window[active_slider_key].update(slider_values[active_face - 1])
                else:
                    values[f'face{next_unlocked_face}'] = 100 - active_slider_value
                    window[f'face{next_unlocked_face}'].update(values[f'face{next_unlocked_face}'])

            elif unlocked_sum == 0 and total > 100:
                #  The unlocked sliders were all 0 and the active slider was increased; decrease active slider
                adjustment = 100 - total
                slider_values[active_face - 1] += adjustment
                window[active_slider_key].update(slider_values[active_face - 1])

            mean_and_deviation(slider_values)
            die_distribution = [_ / 100 for _ in slider_values]

        else:  # Slider is locked, keep value constant
            values[event] = values['locked_values'][int(event[-1]) - 1]
            window[event].update(values[event])

    # ----------------------------------------------------------------------------------------------------------------------
    # Initialize variables
    # ----------------------------------------------------------------------------------------------------------------------
    def get_values(window, values):
        values['locked_values'][active_lock - 1] = values[f'face{active_lock}']
        self.locks[active_lock - 1] = not self.locks[active_lock - 1]
        values['die_distribution'] = [values[f'face{i}'] for i in range(1, 7)]
        mean_and_deviation(values['die_distribution'])

        return values

    
    def add_to_values(window=None, values: dict = None, initialize=False):
        if window is None:
            initialize=True
        if values is None:
            values = {}
        if initialize:
            values['locked_values'] = [0] * 6
            self.locks = [False] * 6
            values['preset_list'] = ['Fair', 'Sloped', 'Valley', 'Hill']
            values['die_distribution'] = random_distribution()
            values['mean'], values['deviation'] = mean_and_deviation([value / 100 for value in values['die_distribution']], get=True, update=False)
            values['dice'] = 3
            values['extra_space'] = 0
            values['logging_UI_text'] = ' '
            return values
        else:
            values = get_values(window=window, values=values)
            return values
'''
