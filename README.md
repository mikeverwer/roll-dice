# Roll Dice

Allows the user to set:

1) An arbitrary probability distribution for a six-sided die,
2) The number of dice to throw per roll, and
3) The number of times to roll.

Shows the probability distribution for the sum of the outcomes and also simulates the rolls.

## The CLT

Suppose you are running an experiment in which the outcomes have an arbitrary probability distribution. This means that the random variable of the experiment is **not** a Normal random variable.  In this example, we use dice for which the probability of each face is randomized.  To reiterate, we can *not* use the Normal Distribution to predict the likely-hood of a single roll of this randomized die.

Simply put, the Central Limit Theorem says; if you run this experiment *N* times, then the ***sum*** of those *N* outcomes will be normally distributed, as long as *N* is large enough.

Test it out by making a very skewed die distribution and setting the number of dice (our *N*) to be small. Press '**Show Sum Distribution**' to see how likely each possible sum is. As you increase *N*, the resulting graph should look more and more *Normal* shaped.
