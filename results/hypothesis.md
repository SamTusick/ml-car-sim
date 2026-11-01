# Experiments

Baseline: results/baseline10 (SIGMA 0.1, MUTATION_RATE 0.1, POOL_FRAC 0.25, pop 50, seeds 0-9)
Baseline primary metric: 4 of 10 seeds reach 2 or more gates

## Current Values

**SIGMA:** 0.1
**MUTATION_RATE:** 0.1
**POOL_FRAC:** 0.25
**pop:** 50
**seeds:** 0-9

Write the hypothesis and commit BEFORE running. Fill in the result after.

| #   | Value changed     | Hypothesis (before run)                                                                                                                                                                                                                                                                                                                                                                    | Result (after run)                                                                                                                                         |
| --- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | SIGMA 0.1 to 0.5  | I predict more seeds reach 2 or more gates (baseline 4 of 10), because larger offsets let children leave the 362 plateau. Mean fitness should drop.                                                                                                                                                                                                                                        | Sigma 0.5 did not detectably change the odds. Better exploration would predict earlier finishes.                                                           |
| 2   | SIGMA 0.1 to 2.0  | I predict that raising SIGMA from 0.1 to 2.0 will raise the number of seeds reaching 2 or more gates (baseline 4/10, sigma 0.5 gave 4/10), because it increases mutation step size, which will affect how children explore. I also expect the final finished count of solving seeds to be lower than 23 to 36, because more crashes will happen because children will follow parents less. | On these 10 seeds, sigma above 0.1 did not increase the number of seeds that progress, 2.0 reduced it, and finishers per solving seed fall as sigma rises. |
| 3   | SIGMA 0.1 to 0.02 |                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                            |
| 4   |                   |                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                            |
