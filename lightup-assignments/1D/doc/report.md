# Introduction

For this assignment the author was asked to implement a Multi-Objective EA (MOEA); unlike past assignments where the EA optimizes over a single objective, MOEA looks at multiple objectives.
In prior assignments the objective was the notion of *fitness*, this time there are three sub-objectives:

1. Percentage of the board that is lit up
2. Number of black cell violations
3. Number of bulbs placed in lit cells

The first sub-objective (percentage of the board that is lit up) should be maximized while the last two should be minimized.
In this assignment, the author implemented a simplified NSGA-II algorithm without crowding.
Additionally, fitness sharing, crowding, and a fourth sub-objective (minimizing the number of bulbs placed) where also required to be implemented by the author.

# MOEA Background

As per Dr. Tauritz's slide deck, NSGA-II works as follows.

1. Initialization
   1. Create an initial population $P_{0}$
   2. Sort $P_{0}$ on the basis of non-domination
   3. Best level is level 1
   4. Fitness is set to level number; lower number, higher fitness
   5. Use Binary (k=2) tournament selection for parent selection
   6. Mutation and Recombination create children $Q_{0}$
2. Primary Loop
   1. Create a population $R_{t}$ by merging the existing population ($P_{t}$) with the new children ($Q_{t}$)
   2. Now sort $R_{t}$ on the basis of non-domination
   3. Create the next generation $P_{t+1}$ by adding the best individuals from $R_{t}$
   4. Create the next set of children ($Q_{t+1}$) by performing Binary Tournament Selection, Recombination and Mutation on $P_{t+1}$

The author's actual implementation is similar but changed a few things.
To allow the new code to integrate easier with the existing code base the author sets the best level to 100; a **higher** level equals a **higher** fitness.

*Domination* can be defined as follows.
An individual **A** is said to dominate an individual **B** iff:

* **A** is no worse than **B** in all objectives
* **A** is strictly better than **B** in at least one objective

# MOEA Implementation

The author has been using a *class-based* approach instead of a *functional* one throughout this assignment series.
Therefore, there is an `Individual` object which stores relevant information such as:

1. Percent of tiles lit
2. Fitness
3. Bulb locations
4. Number of black cell violations
5. Number of bulb intersections
6. Solution Name (unique)

Implementing domination is quite easy with a class setup.
Classes in Python allow you to define special functions referred to as *double-under (dunder)* or *magic functions*.
One example of a dunder function is operator overloading.
To sort a list of individuals based on non-domination one can overload the `<` operator.

```python
def __lt__(self, other):
    a = (self.lit <= other.lit) and \
        (self.bulb_violations >= other.bulb_violations) and \
        (self.black_cell_violations >= other.black_cell_violations)
    b = (self.lit < other.lit) or \
        (self.bulb_violations > other.bulb_violations) or \
        (self.black_cell_violations > other.black_cell_violations)
    return a and b
```

This previous code-snippet allows the next code-snippet to produce a sorted list of individuals using non-domination.

```python
sorted_pop = sorted(population, reverse=True)
```

However to apply the `rank` an additional step is required.
This step can be seen in the `calculate_moea_fitness` function.
One first sorts the passed population and then loops through it applying rank based on `non-domination`.

```python
@ staticmethod
def calculate_moea_fitness(population):
    sorted_pop = sorted(population, reverse=True)

    rank = 100
    for count, ind in enumerate(sorted_pop):
        ind.fitness = rank

        if count + 1 == len(sorted_pop):
            break
        if ind > sorted_pop[count + 1]:
            # new level
            rank -= 1

    return sorted_pop
```

After the rank is applied as the `fitness` for the individual the code runs the same as it did in prior assignments.

# Solution Logging

For this assignment, there were additional changes to the solution file.
Instead of logging the best solution across all runs the best *Pareto Front* and all of its solutions should be logged.
For example, say one has two fronts **P1** and **P2**. **P1** dominates **P2** if the proportion of solutions in **P1** which dominate at least one solution in **P2** is larger than the proportion of solutions in **P2** which dominate at least one solution in **P1**.

This sorting can be similarly achieved in Python as before.
With a custom `ParetoFront` class one can define the `__lt__` function as follows.
Here the function adds up the number of times it dominates the other front and the number of times the other front dominates it.
Finally, the proportions are compared and if the other front dominates the function returns `True`.

```python
def __lt__(self, other):
    total_this_domination_count = 0
    total_other_domination_count = 0
    for other_sol in other.solutions:
        this_domination_count = 0
        other_domination_count = 0
        for solution in self.solutions:
            if solution > other_sol:
                this_domination_count += 1
            elif other_sol > solution:
                other_domination_count += 1
        total_other_domination_count += other_domination_count
        total_this_domination_count += this_domination_count

    return (total_this_domination_count / len(self.solutions)) < \
        (total_other_domination_count / len(other.solutions))
```

<!-- TODO: -->

# MOEA Results

For this assignment, two problems were bundled with the initial repo: D1 and D2.
The author was asked to implement three different configurations and to test them against the two provided problems.
The configurations that were chosen were:

1. Default Configuration
   1. Parent Selection Algorithm: SUS
   2. Recombination: One Point Crossover
   3. Mutation: Creep
   4. Survival Selection: Truncation
   5. Termination Algorithm: Number of Evaluations
   6. Children: 50
   7. Population: 100
   8. Mutation Rate: 0.40
   9. Survival Strategy: +
2. "NSGA" Configuration
   1. Parent Selection Algorithm: Tournament (k=2)
   2. Recombination: One Point Crossover
   3. Mutation: Creep
   4. Survival Selection: Tournament (k=2)
   5. Termination Algorithm: Number of Evaluations
   6. Children: 50
   7. Population: 100
   8. Mutation Rate: 0.40
   9. Survival Strategy: +
3. "Uniform" Configuration
   1. Parent Selection Algorithm: SUS
   2. Recombination: One Point Crossover
   3. Mutation: Creep
   4. Survival Selection: Uniform Random Selection
   5. Termination Algorithm: Number of Evaluations
   6. Children: 50
   7. Population: 100
   8. Mutation Rate: 0.40
   9. Survival Strategy: +

## Default Configuration

One can see in Figure \ref{d1_default} the results of running the default configuration on problem D1.
It is expected that the results for D1 perform better than D2, especially the bulb violations as D2 is more complicated than D1.
This configuration took ~2386 seconds or ~40 minutes to run for D1 and ~2413 seconds or ~40 minutes for D2.

![D1 with default configuration \label{d1_default}](./doc/problem_d1_run.png){ width=500px }

One can see in Figure \ref{d2_default} the results of running the default configuration on problem D2.

![D2 with default configuration \label{d2_default}](./doc/problem_d2_run.png){ width=500px }

## "NSGA" Configuration

This configuration took ~2099 seconds or ~35 minutes to run for D1 and ~2041 seconds or ~34 minutes for D2.

One can see in Figure \ref{d1_nsga} the results of running the NSGA configuration on problem D1.

![D1 with "NSGA" configuration \label{d1_nsga}](./doc/problem_d1_nsga_run.png){ width=500px }

One can see in Figure \ref{d2_nsga} the results of running the NSGA configuration on problem D2.

![D2 with "NSGA" configuration \label{d2_nsga}](./doc/problem_d2_nsga_run.png){ width=500px }

## "Uniform" Configuration

This configuration took ~1833 seconds or ~31 minutes to run for D1 and ~2022 seconds or ~34 minutes for D2.

One can see in Figure \ref{d1_uniform} the results of running the Uniform configuration on problem D1.

![D1 with "Uniform" configuration \label{d1_uniform}](./doc/problem_d1_uniform_run.png){ width=500px }

One can see in Figure \ref{d2_uniform} the results of running the Uniform configuration on problem D2.

![D2 with "Uniform" configuration \label{d2_uniform}](./doc/problem_d2_uniform_run.png){ width=500px }

## Configuration Comparisons

In this section, comparisons are made between the three different configurations.
t-Test statistical analysis was done to compare the two sets (note: this is the same for all comparisons made throughout this document).

### D1

The comparison between the default configuration against the NSGA configuration on problem D1 can be seen in Figure \ref{d1_def_nsga}.

![D1 Default Configuration vs NSGA Configuration \label{d1_def_nsga}](./doc/d1_def_nsga.PNG){ width=500px }

The comparison between the default configuration against the uniform configuration on problem D1 can be seen in Figure \ref{d1_def_uniform}.

![D1 Default Configuration vs Uniform Configuration \label{d1_def_uniform}](./doc/d1_def_uniform.PNG){ width=500px }

The comparison between the NSGA configuration against the uniform configuration on problem D1 can be seen in Figure \ref{d1_nsga_uniform}.

![D1 NSGA Configuration vs Uniform Configuration \label{d1_nsga_uniform}](./doc/d1_nsga_uniform.PNG){ width=500px }

### D2

The comparison between the default configuration against the NSGA configuration on problem D2 can be seen in Figure \ref{d2_def_nsga}.

![D2 Default Configuration vs NSGA Configuration \label{d2_def_nsga}](./doc/d2_def_nsga.PNG){ width=500px }

The comparison between the default configuration against the uniform configuration on problem D2 can be seen in Figure \ref{d2_def_uniform}.

![D2 Default Configuration vs Uniform Configuration \label{d2_def_uniform}](./doc/d2_def_uniform.PNG){ width=500px }

The comparison between the NSGA configuration against the uniform configuration on problem D2 can be seen in Figure \ref{d2_nsga_uniform}.

![D2 NSGA Configuration vs Uniform Configuration \label{d2_nsga_uniform}](./doc/d2_nsga_uniform.PNG){ width=500px }


# Fitness Sharing

For objective **Yellow 1** the author was asked to add an option for *fitness sharing* and investigate and report on how this addition affects performance.
*Fitness sharing*, along with crowding, is a way to increase diversity in populations that may be suffering from low diversity.
Using NSGA-II's rank based fitness one can run into issues with low diversity.
This occurs when a large number of individuals with the same fitness, however, their genes are quite different.
This result can happen in NSGA-II as one applies rank based on levels of non-domination.
Fitness sharing aims to alleviate this issue by generating a new fitness for an individual based on how "close" it is to other individuals.
The formula, as provided in the slides, is as follows:

$f'(i) = \frac{f(i)}{\sum_{j=1}^{\mu} sh(d(i,j))} \quad
sh(d)=\begin{cases}
        1-d/\sigma & \text{if}\ d<\sigma \\
        0 & \text{otherwise}
    \end{cases}$

$\sigma$ is a tunable parameter that correlates to how close an individual should be to another.
Fitness sharing should be calculated right before individual selection occurs for the next generation.

The author uses the Euclidean distance between the three sub-objectives as his distance metrics.
Which can be calculated as follows:
$d(p,q) = \sqrt{\sum_{i=1}^{j}(p_i^2 - q_i^2)^2}$

In this assignment, $j$ is three as there are three sub-objectives.

The author uses the popular Python package SciPy to calculate the Euclidean distance.
Additionally, the fitness sharing formula was tuned as sometimes the one above one can produce results that move beyond the existing rank the individual started at which is not desirable.
Therefore the function has been modified to the following:

$f'(i) = \frac{0.5}{1+\sum_{j=1}^{\mu} sh(d(i,j)) } \quad
sh(d)=\begin{cases}
        1-d/\sigma & \text{if}\ d<\sigma \\
        0 & \text{otherwise}
    \end{cases}$

For the modified formula `1` is added to ensure the fitness doesn't become a level higher than it was when it started and `0.5` can be any values [0,1].
The following Python snippet shows how the author performs fitness sharing.

```python
def fitness_sharing(self, current, population):
    sh_vals = []
    for individual in population:

        # skip current individual from population
        if current.name == individual.name:
            continue

        # generate coordinates used to calculate euclidean distance
        a = (current.lit, current.black_cell_violations,
                current.bulb_violations)
        b = (individual.lit, individual.black_cell_violations,
                individual.bulb_violations)

        distance = scipy.spatial.distance.euclidean(a, b)
        sh_vals.append(self.sh(distance))

    sum_sh = sum(sh_vals)
    fitness = 0.5 / ((sum_sh if sum_sh else 1) + 1)
    return current.fitness + fitness
```

## Results

For both D1 and D2, the same configuration was used which was an adapted version of the "Default" configuration.
The only difference was that fitness sharing was used.

This configuration took ~4851 seconds or ~81 minutes to run for D1 and ~3706 seconds or ~62 minutes for D2.

One can see in Figure \ref{d1_sharing} the results of running the fitness sharing configuration on problem D1.

![D1 with Fitness Sharing \label{d1_sharing}](./doc/problem_d1_sharing_run.png){ width=500px }

One can see in Figure \ref{d2_sharing} the results of running the fitness sharing configuration on problem D2.

![D2 with Fitness Sharing \label{d2_sharing}](./doc/problem_d2_sharing_run.png){ width=500px }

The comparison between the default configuration against the fitness sharing configuration on problem D1 can be seen in Figure \ref{d1_def_sharing}.

![D1 Default Configuration vs Fitness Sharing Configuration \label{d1_def_sharing}](./doc/d1_share.PNG){ width=500px }

The comparison between the default configuration against the fitness sharing configuration on problem D2 can be seen in Figure \ref{d2_def_sharing}.

![D2 Default Configuration vs Fitness Sharing Configuration \label{d2_def_sharing}](./doc/d2_share.PNG){ width=500px }

# Crowding

For objective **Yellow 2** the author was asked to add an option for *crowding* and investigating and reporting on how this addition affects performance.
As stated earlier crowding is another way of increasing diversity in a population.
For the author crowding was more complicated to understand and to implement than fitness sharing.
For the crowding implementation, NSGA-II's crowding was used as a reference. Which is defined as the following

```
l = |I|
for each i, set I[i].distance = 0
for each objective m
    I = sort(I, m)
    I[1].distance = I[l].distance = \inf
    for i = 2 (l - 1)
        I[i].distance += (I[i+1].m - I[i-1].m) / (max(m) - min(m))
```

Essentially, for each objective one will sort the population-based on it, in ascending order.
After sorting one will pick out the boundaries and set their distance to infinity.
Following this, every other individual's distance will be calculated based on the proximity of the surrounding individuals.

For the author's implementation, this was modified, mainly after calculating all the distances they were normalized between 0 and 1.
Values that were marked infinity were normalized between [0.5, 1) other values were normalized between [0, 0.5].
Following the normalization of the distance values the individual's original fitness was increased by this normalized distance metric.
The implementation of crowding can be seen in the following code snippet.
The `update_fitness` function simply adds new values to the existing fitness rank.

```python
def crowding(self, population):
    fronts = self.split_on_pareto_front(population)
    out_distances = {}
    for individuals in fronts.values():
        distance = {individual.name: 0 for individual in individuals}

        distance = self.crowding_lit(individuals, distance)
        distance = self.crowding_black_cell(individuals, distance)
        distance = self.crowding_bulb_violations(individuals, distance)

        out_distances = self.normalize_data(distance, out_distances)

    return self.update_fitness(population, out_distances)
```

All the sub-objective had a different function called, however the logic of the overlying function was the same.
The author was unsure how in Python to achieve a dynamic way to call the same code but to pass a different class instance variable to be used.

```python
def crowding_subobjective(individuals, distance):
    max_val = max([
        individual.subobjective for individual in individuals])
    min_val = min([
        individual.subobjective for individual in individuals])

    sorted_pop = sorted(individuals, reverse=False,
                                        key=lambda ind: ind.subobjective)

    distance[sorted_pop[0].name] = 1000
    distance[sorted_pop[-1].name] = 1000

    for index in range(2, len(sorted_pop) - 1):
        current = sorted_pop[index]
        next_individual = sorted_pop[index + 1]
        prior_individual = sorted_pop[index - 1]
        try:
            distance[current.name] += \
                (next_individual.subobjective - prior_individual.subobjective) / \
                (max_val - min_val)
        except ZeroDivisionError:
            distance[current.name] += 0
    return distance
```

The `normalize_data` function is implemented as follows.
First, it pulls out the infinite distance individuals as they should be normalized in a different range than the non-infinite ones.

```python
def normalize_data(distance, out_distances):
    """ normalizes data between 0 and 1 / val """

    def normalize(data, val):
        # actual function that normalizes data
        # called twice as we want to normalize the non inf values between 0 and some value
        # infinite between some value and .99
        if data:
            return {name: value / (val * max(data.values())) for name, value in data.items()}
        return {}

    # split distances between inf and non inf
    no_inf_distances = {name: value for name,
                        value in distance.items() if value < 1000}
    inf_distances = {name: value for name,
                        value in distance.items() if value >= 1000}

    normalized_no_inf = normalize(no_inf_distances, 2)
    normalized_inf = normalize(inf_distances, 1.0101010101010102)
    out_distances = {**out_distances, **normalized_no_inf, **normalized_inf}
    return out_distances
```

<!-- TODO: -->
## Results

For both D1 and D2 the same configuration was used as for fitness sharing; except crowding was used instead.

This configuration took ~2394 seconds or ~40 minutes to run for D1 and ~2426 seconds or ~40 minutes for D2.

One can see in Figure \ref{d1_crowding} the results of running the crowding configuration on problem D1.

![D1 with Crowding \label{d1_crowding}](./doc/problem_d1_crowding_run.png){ width=500px }

One can see in Figure \ref{d2_crowding} the results of running the crowding configuration on problem D1.

![D2 with Crowding \label{d2_crowding}](./doc/problem_d2_crowding_run.png){ width=500px }

The comparison between the default configuration against the crowding configuration on problem D1 can be seen in Figure \ref{d1_def_crowding}.

![D1 Default Configuration vs Crowding Configuration \label{d1_def_crowding}](./doc/d1_crowding.PNG){ width=500px }

The comparison between the default configuration against the crowding configuration on problem D2 can be seen in Figure \ref{d2_def_crowding}.

![D2 Default Configuration vs Crowding Configuration \label{d2_def_crowding}](./doc/d2_crowding.PNG){ width=500px }


# Minimizing Bulbs

For the **Red 1** objective the author was asked to add a fourth objective; minimizing the number of bulbs placed.
Once added the author would need to investigate and report on how the performance and behavior were impacted by having four objectives rather than three.
Due to the modularity of the author's code, this was relatively easy to implement.
First, a new instance variable had to be added to the `Individual` class called `bulbs` which is the number of bulbs placed for those individuals.

1. Percent of tiles lit
2. Fitness
3. Bulb locations
4. Number of black cell violations
5. Number of bulb intersections
6. A unique name
7. Number of bulbs

After that, the `<` dunder function needed to be updated to include the bulb comparison.

```python
def __lt__(self, other):
    a = (self.lit <= other.lit) and \
        (self.bulb_violations >= other.bulb_violations) and \
        (self.black_cell_violations >= other.black_cell_violations) and \
        (self.bulbs <= other.bulbs)
    b = (self.lit < other.lit) or \
        (self.bulb_violations > other.bulb_violations) or \
        (self.black_cell_violations > other.black_cell_violations) or \
        (self.bulbs < other.bulbs)
    return a and b
```

Additionally, when the individuals are instantiated bulbs would need to be passed to the constructor.

This can be achieved easily by using the *kwargs and args* pattern.
In Python the `*` operator is used to unpack variables, `**` is used to unpack dictionaries.
When using `*` in function calls it unpacks position parameters and `**` is used to unpack named parameters.
Therefore the two following code snippets achieve the same goal.

```python
new_individual = Individual(lit=fitness,\
                            solution=solution,\
                            black_cell_violations=black_cells,\
                            bulb_violations= intersections)
```

```python
kwargs = {'lit': fitness, \
          'solution': solution,\
          'black_cell_violations': black_cells,\
          'bulb_violations': intersections}
new_individual = Individual(**kwargs)
```

The following snippet is how the author allowed the `bulb` variable to be passed to the constructor depending on if the EA was configured for four objectives or three.

```python
fitness, solution, black_cells, intersections = self.initialization_selection(
    board)
kwargs = {'lit': fitness, 'solution': solution,
            'black_cell_violations': black_cells, 'bulb_violations': intersections}
if self.bulb_objective:
    kwargs['bulbs'] = len(solution)

initialize_population.append(Individual(**kwargs))
```

## Results

Running with a fourth objective used the default configuration except there was an extra line specifying to use the fourth objective.

This configuration took ~2433 seconds or ~41 minutes to run for D1 and ~2524 seconds or ~42 minutes for D2.

One can see in Figure \ref{d1_bulbs} the results of running the bulb minimization configuration on problem D1.

![D1 with Fitness Sharing \label{d1_bulbs}](./doc/problem_d1_bulb_run.png){ width=500px }

One can see in Figure \ref{d2_bulbs} the results of running the bulb minimization configuration on problem D2.

![D2 with Fitness Sharing \label{d2_bulbs}](./doc/problem_d2_bulb_run.png){ width=500px }

The comparison between the default configuration against the bulb minimization configuration on problem D1 can be seen in Figure \ref{d1_def_bulb}.

![D1 Default Configuration vs Minimize Bulb Configuration \label{d1_def_bulb}](./doc/d1_bulb.PNG){ width=500px }

The comparison between the default configuration against the bulb minimization configuration on problem D2 can be seen in Figure \ref{d2_def_bulb}.

![D2 Default Configuration vs Minimize Bulb Configuration \label{d2_def_bulb}](./doc/d2_bulb.PNG){ width=500px }

# Conclusion

For this assignment, the author was asked to implement a Multi-Objective EA with the objectives being: percentage of lit cells, the number of black cell constraint violations, and the number of bulbs placed in lit cells.
Additionally, it was requested to implement fitness sharing and crowding for the MOEA.
For bonus points, one could also add a fourth objective; which was minimizing the number of bulbs placed.
Thankfully, due to the modularity of the existing code base, none of these requirements were too difficult to implement.
The most difficult portion of this assignment was probably understanding the math behind the fitness sharing algorithms.
Due to the long run time of the experiments the author ran out of time compiling the report unfortunately cutting some of the statistical analysis short.
