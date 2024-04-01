from types import ModuleType
from classes import mainframe

def mainframe(sg: ModuleType, images: dict, theme, frame: mainframe):
    sg.theme(theme)

    # ----------------------------------------------------------------------------------------------------------------------
    # Layout
    # ----------------------------------------------------------------------------------------------------------------------
    slider_columns = []
    for i in range(1, 7):
        image = sg.Button(image_data=images[f'die{i}'], enable_events=True, key=f'lock{i}')
        slider = sg.Slider(range=(0, 100), orientation='v', size=(5, 20), enable_events=True,  # was (5, 20)
                           default_value=frame.die_distribution[i - 1], key=f'face{i}')
        column = sg.Column([[image], [slider]], element_justification='right')
        slider_columns.append(column)

    # ----------------------------------------------------------------------------------------------------------------------
    # Main Grid
    # ----------------------------------------------------------------------------------------------------------------------
    grid_layout = [
        [sg.Text('The Central Limit Theorem      ', font=("Helvetica", 25))],
        [sg.Text('This program showcases the Central Limit Theorem from probability theory.\n\n'
                 'Use the sliders to set a probability distribution for the dice. Then input the\n'
                 'number of dice to be thrown in each roll, and the number of rolls to perform.')],
        [sg.Frame('Dice Distribution  |  Click on a die face to lock its value', layout=[
                [sg.Push(),
                sg.Frame('', layout=[
                    [sg.Text(f'Mean: {frame.mean:.2f}', font='helvetica 10 bold', background_color='light cyan', k='mean'),
                    sg.Text(f'Standard Deviation: {frame.deviation:.2f}', k='deviation', font='helvetica 10 bold', background_color='light cyan')]
                    ], relief='raised', background_color='light cyan'), sg.Push()
                ],
                slider_columns,
                [sg.Text('_' * 57)],
                [sg.Push(), sg.Text('Preset Distributions'), sg.Combo(frame.preset_list, default_value=None, size=(10, 10),
                                                            enable_events=True, readonly=False, k='preset'),
                sg.Button("Add", k='add preset', p=((0, 50), (0, 0))),
                sg.Button('Randomize', button_color='cyan'), sg.Push()],
                [sg.Text('', font='Courier 1')],
            ], font='Helvetica 12 bold',)
        ],
        [sg.Text('', font='Courier 1')],
        [sg.Text('Number of dice to roll: '), sg.Input(s=4, default_text=3, justification='right', k='dice'),
         sg.Column([
             [sg.Button(image_data=frame.images['up'], key='up')],
             [sg.Button(image_data=frame.images['down'], key='down')]
         ], element_justification="left"),
         sg.Text('Number of rolls: '), sg.Input(s=9, default_text=100, k='rolls')],
        [sg.Text(' ' * 6), sg.Button('Show Sum Distribution', k='theory_button', border_width=2, size=(10, 2),
                                     enable_events=True, font='Helvetica 12', button_color='white on orange'),
         sg.Text(' ' * 10), sg.Button('Pause'),
         sg.Button('Roll the Bones!', k='go', border_width=2, size=(8, 2), enable_events=True,
                   bind_return_key=True, font='Helvetica 12', button_color='white on green'), sg.Text(' ' * 0)]
    ]

    # ----------------------------------------------------------------------------------------------------------------------
    # Logging
    # ----------------------------------------------------------------------------------------------------------------------
    logging_layout = [
        [sg.Text(frame.logging_UI_text, font='Courier 10', justification='left', k='outcome_UI_text'), sg.Push()],
        [sg.Push(),
         sg.Multiline(size=(54, 15),
                      default_text='All the roll outcomes will be printed here!\nThe values describe how often each face appeared.\n',
                      font='Courier 10', expand_x=True, expand_y=True, write_only=True, reroute_stdout=True,
                      reroute_stderr=True,
                      echo_stdout_stderr=True, autoscroll=True, auto_refresh=True, key='log'),
         sg.Push()]
    ]

    grid_layout += logging_layout

    # ----------------------------------------------------------------------------------------------------------------------
    # Graphs 
    # ----------------------------------------------------------------------------------------------------------------------
    con_dx = frame.con_margins[0][0]
    con_dy = frame.con_margins[1][0]
    con_x = frame.con_graph_size[0]
    con_y = frame.con_graph_size[1]
    sim_dx = frame.sim_margins[0][0]
    sim_dy = frame.sim_margins[1][0]
    sim_x = frame.sim_graph_size[0]
    sim_y = frame.sim_graph_size[1]
    plots_layout = [
        [sg.Graph((con_x, con_y), (-con_dx, -con_dy), (con_x - con_dx, con_y - con_dy), background_color='white', key = 'convolution graph',
                  expand_y=True, enable_events=True)],
        [sg.Graph((sim_x, sim_y), (-sim_dx, -sim_dy), (sim_x - sim_dx, sim_y - sim_dy), background_color='white', key = 'simulation graph',
                  expand_y=True, enable_events=True)
        ]
    ]

    # ----------------------------------------------------------------------------------------------------------------------
    # Finalize
    # ----------------------------------------------------------------------------------------------------------------------
    menu_def = [
        ['&About', ['About', 'The CLT']]
    ]

    layout = [
        [sg.Menu(menu_def, key='menu'), sg.Text('')],
        [sg.Column(grid_layout, element_justification='center'), sg.Column(plots_layout)],
    ]

    layout += [[sg.Button('Exit', font='Helvetica 14', button_color='white on red'),
                sg.Text('Created by: Mike Verwer, M.Sc. Mathematics; Prof. Mathematics, Mohawk College')]]

    # ----------------------------------------------------------------------------------------------------------------------
    # Initialize Window
    # ----------------------------------------------------------------------------------------------------------------------

    window = sg.Window(
        'CLT Demonstration', layout, default_element_size=(55, 1), grab_anywhere=True, finalize=True)  # was (60, 1)
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Hotkeys
    # ----------------------------------------------------------------------------------------------------------------------
    return window
    