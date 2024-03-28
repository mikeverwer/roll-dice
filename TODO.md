# To Do

## High priority

### build simulation  

#### Pre-Simulation checklist

- Enough Space?
  - `required_vertical_px = (1.05 * rolls) * P(x); where P(x) is max(P(x) | x in X)`
    - determine line thickness
  - horizontal_px: determine number of bins, bin width

#### Simulation Steps

1. Draw box around graphing area
2. Draw tick marks and labels
3. Roll:
    1. roll the *n* dice and get sum (perhaps display somehow). add to frequency dictionary.
    2. find coordinates for sum: `(sum, frequency['sum'])`
    3. if old_line: -> draw over old line (blue)
    4. draw new line

## Lower Priority

- move to separate files
    . handle_events(sg, window, values) -  *maybe*
    . make_window(sg, values)

## Bug Fixes

- fix mean and deviation after randomizing
