from types import ModuleType
import PySimpleGUI
# from classes import mainframe
import classes as cl

def update_frame(window: PySimpleGUI.Window, frame: cl.mainframe):
    f: cl.mainframe = frame
    f.window = window
    # initialize convolution graph
    f.con_graph = f.window['convolution graph']
    f.convolution.graph = f.con_graph
    f.convolution.make_bars()

    # drag-anywhere exclusions
    drag_exclusions = ['convolution graph', 'simulation graph', 'Pause', 'go', 'add preset', 'Randomize', 'up', 'down']
    drag_exclusions += [f'face{i}' for i in range(1, 7)] + [f'lock{j}' for j in range(1, 7)]
    for item in drag_exclusions:
        f.window[f'{item}'].grab_anywhere_exclude()
    # f.convolution.graph.grab_anywhere_exclude()
    # f.window['simulation graph'].grab_anywhere_exclude()
    # f.window['Pause'].grab_anywhere_exclude()
    # f.window['go'].grab_anywhere_exclude()


def do_binds(window, button_images):
    """
    This is magic code that enables the mouseover highlighting to work.
    """
    for image in button_images:
        window[('hover', image)].bind('<Enter>', 'ENTER')
        window[('hover', image)].bind('<Leave>', 'EXIT')


def Mainframe(sg: PySimpleGUI, images: dict, theme, frame: cl.mainframe):
    sg.theme(theme)
    screen_width, screen_height = sg.Window.get_screen_size()

    # ----------------------------------------------------------------------------------------------------------------------
    # Layout
    # ----------------------------------------------------------------------------------------------------------------------
    slider_columns = [sg.Push()]
    for i in range(1, 7):
        b64_image_data = getattr(frame.images, f'die{i}')
        image = sg.Button(image_data=b64_image_data, enable_events=True, key=f'lock{i}', p=((0, 10), (0, 0)))
        slider = sg.Slider(range=(0, 100), orientation='v', size=(5, 20), enable_events=True,  # was (5, 20)
                           default_value=frame.die_distribution[i - 1], key=f'face{i}', p=((0, 10), (5, 5)))
        column = sg.Column([[image], [slider]], element_justification='right')
        slider_columns.append(column)
    slider_columns.append(sg.T('', p=((0, 10), (0, 0))))
    slider_columns.append(sg.Push())

    # ----------------------------------------------------------------------------------------------------------------------
    # Main Grid
    # ----------------------------------------------------------------------------------------------------------------------
    die_dist_layout = [
                [sg.Push(), sg.Text('Use the sliders to set a probability distribution for the dice.', font='helvetica 10', p=((0, 0), (2, 2))), sg.Push()],
                [sg.Push(),
                sg.Frame('', layout=[
                    [sg.Text(f'Mean: {frame.mean:.2f}', font='helvetica 10 bold', background_color='light cyan', k='mean'),
                     sg.Text(f'Standard Deviation: {frame.deviation:.2f}', k='deviation', font='helvetica 10 bold', background_color='light cyan')]
                    ], relief='raised', background_color='light cyan', p=((0, 0), (0, 4))), sg.Push()
                ],
                slider_columns, 
                [sg.Text('-' * 59, p=((0, 0), (0, 16)))],
                [sg.Push(), sg.Text('Preset Distributions'), sg.Combo(frame.preset_list, default_value=None, size=(10, 10),
                                                            enable_events=True, readonly=False, k='preset'),
                sg.Button(" Add ", k='add preset', p=((16, 50), (0, 0))),
                sg.Button('Randomize', button_color='cyan'), sg.Push()],
                [sg.Text('', font='Courier 1')],
            ]


    grid_layout = [
        [sg.Text('The Central Limit Theorem', font="Helvetica 26 bold")],
        [sg.Frame('Dice Distribution  |  Click on a die face to lock its value', layout=[
                [sg.Push(), sg.Text('Use the sliders to set a probability distribution for the dice.', font='helvetica 10', p=((0, 0), (2, 2))), sg.Push()],
                [sg.Push(),
                sg.Frame('', layout=[
                    [sg.Text(f'Mean: {frame.mean:.2f}', font='helvetica 10 bold', background_color='light cyan', k='mean'),
                    sg.Text(f'Standard Deviation: {frame.deviation:.2f}', k='deviation', font='helvetica 10 bold', background_color='light cyan')]
                    ], relief='raised', background_color='light cyan', p=((0, 0), (0, 4))), sg.Push()
                ],
                slider_columns, 
                [sg.Text('_' * 59, p=((0, 0), (0, 16)))],
                [sg.Push(), sg.Text('Preset Distributions'), sg.Combo(frame.preset_list, default_value=None, size=(10, 10),
                                                            enable_events=True, readonly=False, k='preset'),
                sg.Button(" Add ", k='add preset', p=((16, 50), (0, 0))),
                sg.Button('Randomize', button_color='cyan'), sg.Push()],
                [sg.Text('', font='Courier 1')],
            ], font='Helvetica 12 bold', k='die inputs frame', p=((0, 0), (0, 0)))
        ],
        [sg.Frame(title='', relief='raised', layout=[
                [sg.Text(' Number of dice to roll: ', font='Helvetica 12 bold'), sg.Input(s=4, k='dice', default_text=frame.dice, readonly=False, justification='right', enable_events=True),
                sg.Column([
                    [sg.Button(image_data=frame.images.up, key='up')],
                    [sg.Button(image_data=frame.images.down, key='down')]
                ])]
            ], p=((0, 0), (8, 8))
         )
        ]
        
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

    # ----------------------------------------------------------------------------------------------------------------------
    # Simulation Interface
    # ----------------------------------------------------------------------------------------------------------------------
    sim_input_column_layout = [
        [sg.Text('Number of rolls: ', p=((4, 0), (0, 4))), sg.Input(s=9, default_text=100, k='rolls', p=((0, 0), (0, 4)))],
        [sg.Push(), 
        sg.Button('Pause', button_color='#1b1b1b on darkgrey', font='Helvetica 12 bold', size=(8, 1), border_width=2),
        sg.Button('Roll!', k='go', border_width=2, size=(8, 1), bind_return_key=True, 
                font='Helvetica 12 bold', button_color='white on green'),
        sg.Push()],
    ]
    
    sim_display_column_layout = [
        [sg.Image(data=None, k='dice gif'), sg.Text('test')]
    ]

    sim_inter_layout = [
        [sg.Column(layout=sim_input_column_layout, p=((8, 8), (8, 8))),
        ]
    ]

    # ----------------------------------------------------------------------------------------------------------------------
    # Graphs 
    # ----------------------------------------------------------------------------------------------------------------------

    # novelty_graph_column = sg.Column(layout=[
    #         [sg.Stretch(), novelty_graph, sg.Stretch()]
    #     ], scrollable=True, vertical_scroll_only=True, size=(graph_dimensions['nx'] + 10, desired_window_height), key='novelty column', expand_y=True, expand_x=True, 
    #     sbar_width=10, sbar_arrow_width=10, sbar_relief='flat', sbar_arrow_color=black if mode == 'dark' else white, sbar_background_color=black if mode == 'dark' else white, sbar_trough_color='gray' if mode == 'light' else None
    # )

    con_dx = frame.con_margins[0][0]
    con_dy = frame.con_margins[1][0]
    con_x = frame.con_graph_size[0]
    con_y = frame.con_graph_size[1]
    sim_dx = frame.sim_margins[0][0]
    sim_dy = frame.sim_margins[1][0]
    sim_x = frame.sim_graph_size[0]
    sim_y = frame.sim_graph_size[1]

    convolution_graph_layout = [
        [sg.Push(), sg.Graph((con_x, con_y), (-con_dx, -con_dy), (con_x - con_dx, con_y - con_dy), background_color='white', key = 'convolution graph',
                expand_y=True, expand_x=True, enable_events=True), sg.Push()]
        ]

    sim_layout = [
        [sg.Graph((sim_x, sim_y), (-sim_dx, -sim_dy), (sim_x - sim_dx, sim_y - sim_dy), background_color='#f0f0f0', key = 'simulation graph',
                  expand_y=True, enable_events=True)]
    ]

    smallest_height = 630
    sim_column = [
        [sg.Stretch(), 
         sg.Column(layout=sim_layout, scrollable=True, vertical_scroll_only=True, size=(frame.sim_graph_size[0], smallest_height), key='sim column',
                   expand_x=True, expand_y=True, vertical_alignment='top',
                   sbar_width=12, sbar_arrow_width=6, sbar_relief='flat', sbar_arrow_color='#1b1b1b', sbar_background_color='white', sbar_trough_color='#dcdcdc'
                   ),
         sg.Stretch()]
    ]
    sim_layout = sim_column

    # ----------------------------------------------------------------------------------------------------------------------
    # Finalize
    # ----------------------------------------------------------------------------------------------------------------------    
    layout =[
        []
    ]
    
    hoverable_buttons = ['author', 'menubar_CLT']
    menu_def = [
        [sg.Image(data=images.menubar1), sg.Image(data=frame.images.menubar_CLT, enable_events=True, key=('hover', 'menubar_CLT')), sg.Image(data=images.menubar2), 
         sg.Push(), sg.Image(data=images.menubar1_r), sg.Image(data=images.author, enable_events=True, key=('hover', 'author'))]
    ]

    sim_layout += sim_inter_layout

    grid_layout += [[sg.TabGroup([[sg.Tab(frame.convolution_title, layout=convolution_graph_layout, k='dist tab'),
                                   sg.Tab('    Log    ', logging_layout, k='log tab')
                                   ]],
                                font='Helvetica 12 bold', focus_color='white', border_width=0),
    ]]

    layout += menu_def

    layout += [
        [sg.Column(grid_layout, element_justification='center', vertical_alignment='top'), sg.Column(sim_layout)],
    ]

    # ----------------------------------------------------------------------------------------------------------------------
    # Initialize Window
    # ----------------------------------------------------------------------------------------------------------------------

    window = sg.Window(
        'CLT Demonstration', layout, grab_anywhere=True, element_padding=0, margins=(0, 0), finalize=True, font='helvetica 10 bold', 
        border_depth=0, icon=frame.images.lock6)  # was (60, 1)
    do_binds(window, hoverable_buttons)
    update_frame(window, frame)
    window['sim column'].Widget.canvas.yview_moveto(1.0)
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Hotkeys
    # ----------------------------------------------------------------------------------------------------------------------
    return window
    