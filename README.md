# Roll Dice

This program illustrates the Central Limit Theorem by using the example of throwing different amounts of dice, where the dice to be thrown have matching, but arbitrary, probability distributions.

Allows the user to set:

1) An arbitrary probability distribution for a six-sided die,
2) The number of dice to throw per roll, and
3) The number of times to roll.

Shows the probability distribution for the sum of the outcomes and also simulates the rolls. Both the theoretical distribution and the simulation are interactive. You can select any of the rolls and it will display the outcome of each individual die that was rolled as well as the sum. Selecting one of the bars on the distribution will display the likelihood of that sum being rolled and also highlight the corresponding bin in the simulation, if the distribution still matches the simulation.

## Description

The user can choose an arbitrary probability distribution for the faces of a six sided die by using auto-adjusting sliders.  There are also some useful presets and a randomizer.  The user also enters the number of dice to roll per trial, $n$, and the number of trials to simulate, *T*.  

As you change the number of dice or the distribution of the die, a graph displaying the *theoretical probability distribution* for throwing that many dice is updated.  This graph is called the **convolution** of the die distribution.  You can interact with it by clicking the bars, which will display the outcome and its likelihood.  

As the theorem proposes, the theoretical prediction becomes more and more *Normal* shaped as the number of dice to be rolled increases.  Even the most skewed starting die distributions become *Normal* by 30 dice per roll.

Press `Roll the Bones!` to begin the simulation.  The outcome of each die is displayed as the rolls occur, and each roll is place as a block on an axis of all the possible outcomes.  This builds a dot-plot of all the rolls.  Each roll is remembered and can be displayed by selecting its block.

Selecting a bar on the convolution graph, or clicking on one of the bins below the x-axis of the simulation, will highlight that column on both graphs.  This is useful to keep track of a specific outcome as the rolls occur, and compare the predicted outcomes to the actual ones.

![UI Screen Shot](/assets/roll-dice-ss.png)

## The CLT

Suppose you are running an experiment in which the outcomes have an arbitrary probability distribution. This means that the random variable of the experiment is **not** a Normal random variable.  In this example, we use dice for which the probability of each face is randomized.  To reiterate, we can *not* use the Normal Distribution to predict the likely-hood of a single roll of this randomized die.

Simply put, the Central Limit Theorem says; if you run this experiment $N$ times, then the ***sum***$^{[1]}$  of those $N$ outcomes will be normally distributed, as long as $N$ is large enough.  Furthermore, the mean of the sum distribution will be $N\cdot\mu$, where $\mu$ is the mean of the original die; and the standard deviation of the sum is $\sqrt{N}\cdot\sigma$, where $\sigma$ is the standard deviation of the original die.

## Licensing

    This product includes PySimpleGUI (https://PySimpleGUI.com).  PySimpleGUI
    is Copyright (c) PySimpleSoft, Inc. and/or its licensors.  Use of
    PySimpleGUI is subject to the license terms available at
    https://PySimpleGUI.com/eula

    PYSIMPLEGUI IS PROVIDED "AS IS," WITHOUT ANY WARRANTIES, WHETHER EXPRESS OR
    IMPLIED. PYSIMPLESOFT DISCLAIMS ALL IMPLIED WARRANTIES, INCLUDING WITHOUT
    LIMITATION THE IMPLIED WARRANTIES OF NONINFRINGEMENT, TITLE,
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
