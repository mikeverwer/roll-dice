# To Do

- add x grid marks to simulation graph
- fix "fair" die being unfair
- pre-sim checklist
- trim x-axes
- rework the window
  - Add roll display graph, maybe even animate the rolls with different dice png's

## High priority

- make axes for both graphs, think about partitioning the percentage.

### Convolution Class

- migrate all convolution related functions from mainframe to convolution
- trim outcomes
- selecting bar:
  - draws a highlight of the column in the sim graph
  - displays probability in the conv-graph- top space

### Simulation Complete

#### Pre-Simulation checklist

- Enough Space?
  - `required_vertical_px = (1.05 * rolls) * E[x]; where E[x] expected value/mean of convolution`
    - determine line thickness
  - horizontal_px: determine number of bins, bin width

## Lower Priority

- move to separate files
    . handle_events(sg, window, values) -  *maybe*

## Bug Fixes

- fix mean and deviation after randomizing
- changing the sliders should reset the preset combo to be blank
