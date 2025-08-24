"""
Filename: alife.py
Author: Mahitha Gudipaty

Description:
Simulates an artificial life ecosystem with rabbits and foxes.
Rabbits eat grass to survive and reproduce.
Foxes eat rabbits to survive and reproduce.
Both species face starvation if they go too many generations without food.

Model Assumptions:
- Field size: 65 x 65
- Grass regrowth rate: 3.5% chance per cell per generation

Rabbits:
- Initial population: 50
- Maximum offspring per generation: 1
- Starvation level: 3 generations without food
- Reproduction threshold: 2 units of food

Foxes:
- Initial population: 35
- Maximum offspring per generation: 3
- Starvation level: 12 generations without food
- Reproduction threshold: 1 unit of food

Output:
An animated matplotlib simulation and population dynamics over time.
"""

import random as rnd
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Field and simulation parameters
ARRSIZE = 65
FIGSIZE = 6
INIT_RABBITS = 50
INIT_FOXES = 35
GRASS_RATE = 0.035

# Display codes
COLOR_EMPTY = 0
COLOR_GRASS = 1
COLOR_RABBIT = 2
COLOR_FOX = 3


class Animal:
    """
    Represents a rabbit or fox with movement, hunger, reproduction, and survival logic.
    """
    def __init__(self, species, max_offspring=1, starvation_level=1, reproduction_level=1):
        """
        Initializes an Animal instance (either rabbit or fox) with species-specific traits.

        Parameters:
            species (str): Type of animal, either "rabbit" or "fox".
            max_offspring (int): Maximum number of offspring this animal can produce.
            starvation_level (int): Number of generations the animal can survive without food.
            reproduction_level (int): Minimum amount of food required to reproduce.
        """
        self.species = species
        self.max_offspring = max_offspring
        self.starvation_level = starvation_level
        self.reproduction_level = reproduction_level

        self.hunger = 0  # counts how many generations the animal has gone unfed
        self.eaten = 0  # amount of food consumed in the current generation
        self.alive = True  # whether the animal is still alive

        self.x = rnd.randrange(0, ARRSIZE)  # x-coordinate in the field (random start)
        self.y = rnd.randrange(0, ARRSIZE)  # y-coordinate in the field (random start)

    def move(self):
        """
        Moves the animal randomly in one of the eight directions or stays in place.
        Wraps around the field edges to simulate a toroidal grid.
        """
        self.x = (self.x + rnd.choice([-1, 0, 1])) % ARRSIZE  # move left, stay, or right with wrap-around
        self.y = (self.y + rnd.choice([-1, 0, 1])) % ARRSIZE  # move up, stay, or down with wrap-around

    def eat(self, amount):
        """
        Increases the amount of food the animal has consumed and resets hunger to zero.

        Parameters:
            amount (int): The amount of food consumed at the current location.
        """
        self.eaten += amount
        self.hunger = 0

    def starve(self):
        """
        Increments the animal's hunger level by one. If the hunger exceeds or equals
        the starvation threshold, marks the animal as dead.
        """
        self.hunger += 1  # increase hunger after not eating this generation
        if self.hunger >= self.starvation_level:
            self.alive = False  # animal dies if hunger exceeds allowed limit

    def can_reproduce(self):
        """
        Checks whether the animal has eaten enough to reproduce.

        Returns:
        bool: True if the animal can reproduce, False otherwise.
        """
        return self.eaten >= self.reproduction_level

    def reproduce(self):
        """
        Generates a list of offspring (deep copies of the parent) based on
        the animal's max_offspring value. Resets the eaten counter.

        Returns:
            list: A list of new Animal instances representing offspring.
        """

        self.eaten = 0  # reset food count after reproduction
        return [copy.deepcopy(self) for _ in
                range(rnd.randint(0, self.max_offspring))]  # create a random number of offspring (deep copies)


class Field:
    """
    A 2D environment where grass grows and animals interact.
    Manages feeding, movement, death, and reproduction.
    """
    def __init__(self):
        """
        Initializes the simulation field with grass and empty lists for rabbits and foxes.
        """
        self.field = np.ones((ARRSIZE, ARRSIZE), dtype=int)
        self.rabbits = []
        self.foxes = []

    def add_animal(self, animal):
        """
        Adds an animal to the appropriate population list in the field based on its species.

        Parameters:
            animal (Animal): The Animal instance to add to the field.

        Returns:
            None
        """

        if animal.species == "rabbit":
            self.rabbits.append(animal)  # add to rabbit population
        elif animal.species == "fox":
            self.foxes.append(animal)  # add to fox population

    def move_animals(self):
        """
        Moves all rabbits and foxes in the field one step in a random direction.
        """

        for a in self.rabbits + self.foxes:
            a.move()

    def grow_grass(self):
        """
        Regrows grass at each grid cell with a probability defined by GRASS_RATE.
        """

        grow = (np.random.rand(ARRSIZE, ARRSIZE) < GRASS_RATE).astype(
            int)  # generate new grass based on growth probability
        self.field = np.maximum(self.field,
                                grow)  # regrow grass only where it's currently missing (preserve existing grass)

    def feed_rabbits(self):
        """
        Allows each rabbit to consume grass at its current location.
        If no grass is present, the rabbit's hunger level increases.
        """

        for r in self.rabbits:
            if self.field[r.x, r.y] == 1:  # if grass is present at rabbit's location
                r.eat(1)  # rabbit eats the grass
                self.field[r.x, r.y] = 0  # remove the grass from the field
            else:
                r.starve()  # rabbit didn't eat, increase hunger

    def feed_foxes(self):
        """
        Allows foxes to eat any rabbits present at their current location.
        All rabbits at a fox's position are consumed. If no rabbits are present,
        the fox's hunger increases.
        """

        # Efficient rabbit lookup by (x, y)
        rabbit_locations = {}
        for r in self.rabbits:
            rabbit_locations.setdefault((r.x, r.y), []).append(r)  # group rabbits by location

        for f in self.foxes:
            loc = (f.x, f.y)
            if loc in rabbit_locations:  # if fox is at a location with rabbits
                for r in rabbit_locations[loc]:
                    r.alive = False  # all rabbits at this location are eaten
                f.eat(len(rabbit_locations[loc]))  # fox gains food based on number of rabbits eaten
            else:
                f.starve()  # no rabbits found — hunger increases

    def remove_dead(self):
        """
        Removes any rabbits or foxes from the population lists that are no longer alive.
        """

        self.rabbits = [r for r in self.rabbits if r.alive]
        self.foxes = [f for f in self.foxes if f.alive]

    def reproduce_animals(self):
        """
        Handles reproduction for both rabbits and foxes.
        Adds offspring to the population if reproduction conditions are met.
        """

        born_rabbits = []  # list to hold new rabbit offspring
        born_foxes = []  # list to hold new fox offspring

        for r in self.rabbits:
            if r.can_reproduce():  # check if rabbit has enough food to reproduce
                born_rabbits.extend(r.reproduce())  # add its offspring to the list

        for f in self.foxes:
            if f.can_reproduce():  # check if fox has enough food to reproduce
                born_foxes.extend(f.reproduce())  # add its offspring to the list

        self.rabbits.extend(born_rabbits)  # add new rabbits to the population
        self.foxes.extend(born_foxes)  # add new foxes to the population

    def generation(self):
        """
        Executes a full simulation step:
        - Moves all animals
        - Handles feeding
        - Removes dead animals
        - Handles reproduction
        - Regrows grass
        """

        self.move_animals()
        self.feed_rabbits()
        self.feed_foxes()
        self.remove_dead()
        self.reproduce_animals()
        self.grow_grass()

    def get_display_array(self):
        """
        Creates a copy of the field and overlays rabbit and fox positions for visualization.

        Parameters:
            None

        Returns:
            np.ndarray: A 2D array representing the combined state of grass, rabbits, and foxes.
        """

        display = self.field.copy()  # start with a copy of the current grass field

        for r in self.rabbits:
            display[r.x, r.y] = COLOR_RABBIT  # overlay rabbit positions on the field

        for f in self.foxes:
            display[f.x, f.y] = COLOR_FOX  # overlay fox positions on top of rabbits or grass

        return display  # return the combined display array for rendering


def animate(i, field, im, rabbit_counts, fox_counts):
    """
    Runs one animation frame by updating the ecosystem and refreshing the plot.

    Parameters:
        i (int): The current frame number.
        field (Field): The field instance managing the ecosystem.
        im (AxesImage): The image object used for rendering the animation.
        rabbit_counts (list): List to store rabbit population over time.
        fox_counts (list): List to store fox population over time.

    Returns:
        tuple: The updated image object (required by FuncAnimation).
    """

    field.generation()  # run one full generation of the simulation (move, feed, reproduce, etc.)
    im.set_array(field.get_display_array())  # update the image with the new field state

    plt.title(
        f"Gen: {i}  Rabbits: {len(field.rabbits)}  Foxes: {len(field.foxes)}")  # update plot title with current generation and population counts

    rabbit_counts.append(len(field.rabbits))  # log current rabbit population
    fox_counts.append(len(field.foxes))  # log current fox population

    return im,  # return updated image (required format for FuncAnimation)


def main():
    """
    Initializes the field, populates it with animals, runs the simulation,
    and plots the population dynamics over time.
    """

    field = Field()  # create a new field instance (ecosystem)

    # Initialize rabbits with given parameters
    for _ in range(INIT_RABBITS):
        field.add_animal(Animal("rabbit", max_offspring=1, starvation_level=3, reproduction_level=2))

    # Initialize foxes with given parameters
    for _ in range(INIT_FOXES):
        field.add_animal(Animal("fox", max_offspring=3, starvation_level=12, reproduction_level=1)
)

    rabbit_counts = []  # track rabbit population over generations
    fox_counts = []  # track fox population over generations

    # Set up the figure and initial image for animation
    fig = plt.figure(figsize=(FIGSIZE, FIGSIZE))
    cmap = plt.cm.get_cmap('nipy_spectral', 4)  # use a custom colormap with 4 color levels
    im = plt.imshow(field.get_display_array(), cmap=cmap, interpolation='nearest', vmin=0, vmax=3)

    # Create the animation using FuncAnimation
    anim = animation.FuncAnimation(fig, animate, fargs=(field, im, rabbit_counts, fox_counts),
                                   frames=150, interval=100)
    plt.show()  # display the animation window

    # Time series plot of population trends after the animation finishes
    plt.figure(figsize=(10, 4))
    plt.plot(rabbit_counts, label="Rabbits", color='green')  # plot rabbit population over time
    plt.plot(fox_counts, label="Foxes", color='red')  # plot fox population over time
    plt.xlabel("Generation")
    plt.ylabel("Population")
    plt.title("Rabbit and Fox Population Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()  # display the final population plot


if __name__ == '__main__':
    main()
