import PySimpleGUI as sg
import classes as cl

def update_frame(window: sg.Window, frame: cl.Mainframe):
    f: cl.Mainframe = frame
    f.window = window
    f.window.set_min_size((810, 765))
    screen_width, screen_height = sg.Window.get_screen_size()
    f.window.size = ((0.85 * screen_width, 0.75 * screen_height))
    f.resize_graphs()

    # initialize convolution graph
    f.con_graph = f.window['convolution graph']
    f.convolution.graph = f.con_graph
    f.convolution.make_bars()

    # drag-anywhere exclusions
    drag_exclusions = ['convolution graph', 'simulation graph', 'Pause', 'go', 'add preset', 'Randomize', 'up', 'down']
    drag_exclusions += [f'face{i}' for i in range(1, 7)] + [f'lock{j}' for j in range(1, 7)]
    for item in drag_exclusions:
        f.window[f'{item}'].grab_anywhere_exclude()


def do_binds(window, button_images):
    for image in button_images:  # key for image button must be tuple with ('hover', key)
        window[('hover', image)].bind('<Enter>', 'ENTER')
        window[('hover', image)].bind('<Leave>', 'EXIT')
    window.bind("<Configure>", "resize")


def Mainframe_func(sg: sg, images: dict, theme, frame: cl.Mainframe):
    sg.theme(theme)

    # ----------------------------------------------------------------------------------------------------------------------
    # Screen and Graph Sizing
    # ----------------------------------------------------------------------------------------------------------------------
    screen_width, screen_height = sg.Window.get_screen_size()
    frame.sim_graph_size = (screen_width - 500, 10_000)  # 500 px required for left column + random extra space
    frame.con_graph_size = (450, 325)  # should fit within any screensize
    frame.sim_viewing_height = screen_height - 105  # the vertical number of pixels of the sim graph that get displayed


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
                [sg.Text('\u2014' * 30, p=((0, 0), (0, 16)))],
                [sg.Push(), sg.Text('Preset Distributions'), sg.Combo(frame.preset_list, default_value=None, size=(10, 10),
                                                            enable_events=True, readonly=False, k='preset'),
                sg.Button(" Add ", k='add preset', p=((16, 50), (0, 0))),
                sg.Button('Randomize', button_color='cyan'), sg.Push()],
                [sg.Text('', font='Courier 1')],
            ]
    
    sim_input_column_layout = [
        [sg.Text('Number of rolls: ', p=((4, 0), (0, 4))), sg.Input(s=9, default_text=200, k='rolls', p=((0, 0), (0, 4)))],
        [sg.Push(), 
        sg.Button('Pause', button_color='#1b1b1b on darkgrey', font='Helvetica 12 bold', size=(8, 1), border_width=2),
        sg.Button('Roll!', k='go', border_width=2, size=(8, 1), bind_return_key=True, 
                font='Helvetica 12 bold', button_color='white on green'),
        sg.Push()],
    ]

    # sim_inter_layout = [
    #     [sg.Column(layout=sim_input_column_layout, p=((8, 8), (8, 8))),
    #     ]
    # ]

    grid_layout = [
        [sg.Text('The Central Limit Theorem', font="Helvetica 26 bold")],
        [sg.Frame('Dice Distribution  |  Click on a die face to lock its value', layout=die_dist_layout, font='Helvetica 12 bold', k='die inputs frame', p=((0, 0), (0, 0)))],
        [sg.Frame(title='', relief='raised', layout=[
                [sg.Text(' Number of dice to roll: ', font='Helvetica 12 bold'), sg.Input(s=4, k='dice', default_text=frame.dice, readonly=False, justification='right', enable_events=True),
                sg.Column([
                    [sg.Button(image_data=frame.images.up, key='up')],
                    [sg.Button(image_data=frame.images.down, key='down')]
                ])]
            ], p=((0, 12), (8, 8))
         ),
         sg.Frame(title=None, layout=sim_input_column_layout, p=(4, 8), relief='raised')
        ]
        
    ]

    # ----------------------------------------------------------------------------------------------------------------------
    # Logging
    # ----------------------------------------------------------------------------------------------------------------------
    logging_layout = [
        [sg.Button('Clear'), sg.Push()],
        [sg.Push(),
         sg.Multiline(size=(54, 15),
                      default_text='Logging information will be printed here.\nTurn on `logging` or `full_logging` to see event/values log.\n',
                      font='Courier 10', expand_x=True, expand_y=True, write_only=True, reroute_stdout=True,
                      reroute_stderr=True,
                      echo_stdout_stderr=True, autoscroll=True, auto_refresh=True, key='log'),
         sg.Push()]
    ]

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

    convolution_graph_layout = [
        [sg.Push(), sg.Graph((con_x, con_y), (-con_dx, -con_dy), (con_x - con_dx, con_y - con_dy), background_color='white', key = 'convolution graph',
                expand_y=True, expand_x=True, enable_events=True), sg.Push()]
        ]

    sim_layout = [
        [sg.Graph((sim_x, sim_y), (-sim_dx, -sim_dy), (sim_x - sim_dx, sim_y - sim_dy), background_color='#f0f0f0', key = 'simulation graph',
                  expand_y=True, enable_events=True)]
    ]

    sim_column = [
        [sg.Stretch(), 
         sg.Column(layout=sim_layout, scrollable=True, vertical_scroll_only=True, size=(frame.sim_graph_size[0], frame.sim_viewing_height), key='sim column',
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

    # sim_layout += sim_inter_layout

    grid_layout += [[sg.TabGroup([[sg.Tab(frame.convolution_title, layout=convolution_graph_layout, k='dist tab'),
                                   sg.Tab('  Log  ', logging_layout, k='log tab')
                                   ]],
                                font='Helvetica 12 bold', focus_color='white', border_width=0, ),
    ]]

    layout += menu_def

    layout += [
        [sg.Column(grid_layout, element_justification='center', vertical_alignment='center'), sg.Column(sim_layout)],
    ]

    layout[-1].append(sg.Sizegrip())

    # ----------------------------------------------------------------------------------------------------------------------
    # Initialize Window
    # ----------------------------------------------------------------------------------------------------------------------
    #  min size (810, 765)
    window = sg.Window(
        'CLT Demonstration', layout, grab_anywhere=True, element_padding=0, margins=(0, 0), finalize=True, font='helvetica 10 bold', 
        border_depth=0, icon=frame.images.lock6, resizable=True, location=(0, 0), size=(int(0.85 * screen_width), int(0.75 * screen_height)))  # was (60, 1)
    do_binds(window, hoverable_buttons)
    update_frame(window, frame)
    window['sim column'].Widget.canvas.yview_moveto(1.0)
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Hotkeys
    # ----------------------------------------------------------------------------------------------------------------------
    return window
    