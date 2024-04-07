# To Do

- display selected bar info on conv_graph
- trim x-axes
- rework the window
- tell sim about selected convolution bar if the outcomes lengths match (or maybe endpoints)

## High priority

### Convolution Class

- migrate all convolution related functions from mainframe to convolution (done?)
- trim outcomes
- selecting bar:
  - draws a highlight of the column in the sim graph
  - displays probability in the conv-graph- top space

#### Selecting Bar

- maybe a class method that takes in a simulation as an argument

### Simulation Complete

## Lower Priority

- move to separate files:
  - handle_events(sg, window, values) -  *maybe*
    - event_handler class
    - in mainframe: `self.maestro = event_handler(self)`
    - in event_handler class:

        ```python
        def __init__(self, frame):
          self.frame = mf

        def Handle(self, event)
          # code from main goes here, replacing mf with self.mf
        ```

## Bug Fixes

- fix "fair" die being unfair
- fix mean and deviation after randomizing
- changing the sliders should reset the preset combo to be blank
