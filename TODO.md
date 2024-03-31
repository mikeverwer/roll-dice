# To Do

- add x grid marks to simulation graph
- convert convolution display to graph that auto-updates when the die distribution changes
- fix "fair" die being unfair
- pre-sim checklist
- trim x-axes
- rework the window
  . make convolution display smaller, where log is now
  . raise simulation graph and add controls/roll display below

## High priority

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
