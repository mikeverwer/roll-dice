# Roll Dice

This program illustrates the Central Limit Theorem by using the example of throwing different amounts of dice, where the dice to be thrown have matching, but arbitrary, probability distributions.

Allows the user to set:

1) An arbitrary probability distribution for a six-sided die,
2) The number of dice to throw per roll, and
3) The number of times to roll.

Shows the probability distribution for the sum of the outcomes and also simulates the rolls. Both the theoretical distribution and the simulation are interactive. You can select any of the rolls and it will display the outcome of each individual die that was rolled as well as the sum. Selecting one of the bars on the distribution will display the likelihood of that sum being rolled and also highlight the corresponding bin in the simulation, if the distribution still matches the simulation.

## The CLT

Suppose you are running an experiment in which the outcomes have an arbitrary probability distribution. This means that the random variable of the experiment is **not** a Normal random variable.  In this example, we use dice for which the probability of each face is randomized.  To reiterate, we can *not* use the Normal Distribution to predict the likely-hood of a single roll of this randomized die.

Simply put, the Central Limit Theorem says; if you run this experiment *N* times, then the ***sum*** of those *N* outcomes will be normally distributed, as long as *N* is large enough.

Test it out by making a very skewed die distribution and setting the number of dice (our *N*) to be small. As you increase the number of die, watch the graph in the bottom left become more and more "normal" shaped.

## Licensing

    This product includes PySimpleGUI (https://PySimpleGUI.com).  PySimpleGUI
    is Copyright (c) PySimpleSoft, Inc. and/or its licensors.  Use of
    PySimpleGUI is subject to the license terms available at
    https://PySimpleGUI.com/eula

    PYSIMPLEGUI IS PROVIDED "AS IS," WITHOUT ANY WARRANTIES, WHETHER EXPRESS OR
    IMPLIED. PYSIMPLESOFT DISCLAIMS ALL IMPLIED WARRANTIES, INCLUDING WITHOUT
    LIMITATION THE IMPLIED WARRANTIES OF NONINFRINGEMENT, TITLE,
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
