# Predator Prey Ecosystem Simulation

A lightweight, animated predator prey simulation written in Python. Rabbits roam a 2D grid, eat grass, survive or starve, and reproduce. Foxes hunt rabbits and face the same survival and reproduction constraints. The world is a toroidal grid, so movement wraps around edges for continuous motion. 

## **Features:**

* Animated 2D grid with grass, rabbits, and foxes
* Stochastic movement and feeding with starvation logic
* Reproduction based on consumed food
* Efficient predator feeding using location indexing
* Automatic time series plot of population counts after the run finishes

## World and species:

* Grid size is 65 by 65. Grass regrows each generation with probability 0.035 per cell. 
* Default populations: 50 rabbits and 35 foxes. 
* Color legend in the visualization: 0 empty, 1 grass, 2 rabbit, 3 fox. 


## Animals:
* All animals share the same class and differ by parameters.
* Each animal tracks hunger and food consumed this generation. If it fails to eat for too long it dies. Reproduction requires meeting a food threshold. 
* Reproduction creates a random number of offspring up to max_offspring. Consumed food resets after reproducing. 

## Feeding:

* Rabbits eat grass at their location if present. Otherwise they get hungrier. 
* Foxes eat all rabbits at their current location using an indexed lookup by coordinates for speed. If no rabbits are present they get hungrier. 

## Generation loop:

* Each generation runs in this order: move, feed rabbits, feed foxes, remove dead, reproduce, regrow grass.

## Output:

* Live animation of the grid using a 4 level colormap
* Title overlays the generation counter and current population sizes
* A line plot appears at the end with rabbit and fox counts over time