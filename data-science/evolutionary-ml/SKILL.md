---
name: evolutionary-ml
description: "Evolutionary ML: GA, NEAT, tournaments, parallel eval."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [evolutionary-algorithms, neuroevolution, genetic-algorithms, NEAT, tournament-evaluation, parallel-simulation, population-based-training]
    category: data-science
    related_skills: [python-data-science, python-craft, weights-and-biases]
---

# Evolutionary ML: GA, Neuroevolution, Tournament Evaluation

Practical guide for evolutionary approaches to ML — from simple genetic algorithms over fixed-weight vectors to NEAT-style topology evolution and tournament-based evaluation. Covers the patterns that show up repeatedly in evolved-agent projects: genome representation, selection/crossover/mutation, parallel evaluation, Elo tracking, speciation, and the common defects that silently kill learning.

## When to Use

- Training agents via evolution rather than gradient descent (game AI, control policies, symbolic regression)
- Evolving neural network topologies (NEAT, architecture search)
- Tournament or match-based evaluation where fitness comes from head-to-head results (ELO, Swiss, round-robin)
- Population-based hyperparameter search or policy search
- Any project where the "model" is a genome that gets evaluated by running it, not by computing a loss gradient

**Don't use** as a replacement for gradient-based training when you have a differentiable loss and reasonable batch size — evolution is expensive per unit of information. Use it when the problem is non-differentiable, the environment is a simulator/game, or you specifically want the diversity/exploration properties of a population.

## Core Concepts

### Genome vs phenotype

The genome is what evolution operates on — the thing that gets mutated, crossed over, and selected. The phenotype is what actually runs in the environment. In a simple GA, they're the same (the genome is the weight vector). In NEAT, the genome is a list of connection genes and the phenotype is the built network. Keep the distinction clear: mutations happen on the genome, evaluation happens on the phenotype.

### Fitness — what are you selecting for?

Fitness must be a scalar that ranks individuals. The hard part is usually not computing it but making it *comparable* across evaluations:

- **Shared random numbers** across the population in a generation so fitness differences reflect genome differences, not luck.
- **Common opponents** in tournament evaluation — don't let agent A play a different deck sequence than agent B.
- **Elo over raw win rate** when the population shifts over time — raw fitness isn't comparable between generations if the field changes.

### Parallel evaluation

Evolution is embarrassingly parallel at the match level. The typical structure:

1. Generate a list of (agent_a, agent_b, seed, config) tasks.
2. Dispatch to a worker pool (multiprocessing, thread pool for I/O-bound, or a cluster).
3. Collect results, aggregate per-agent fitness.

Watch for: shared RNG state across workers (each worker should have its own seeded RNG, not a shared global), result ordering (tag each task so you can reassemble), and failure handling (a crashed match shouldn't kill the generation — log it and score it as a loss or skip).

## Simple Genetic Algorithm

### Genome representation

For a fixed-architecture policy, the genome is typically a flat vector:

```python
import numpy as np

genome_size = 2311  # example: 64*32 + 32 + 32*5 + 5 + 32*2 + 2
def random_genome() -> np.ndarray:
    return np.random.randn(genome_size).astype(np.float32) * 0.1
```

For structured genomes (e.g., separate layers, or a tree), use a dataclass or a list of arrays and write your own crossover/mutation. The key is that crossover and mutation operate on the *same* representation you select on.

### Selection

```python
def tournament_select(population, fitnesses, k=3, random_state=None):
    """Pick one parent via k-tournament."""
    rng = np.random.default_rng(random_state)
    indices = rng.choice(len(population), size=k, replace=False)
    winner = indices[np.argsort(fitnesses[indices])[-1]]
    return population[winner].copy()
```

Common selectors:

| Selector | Behavior | Watch for |
|---|---|---|
| Tournament (k=2–5) | Pick k random, take best | Small k = weak pressure; large k = premature convergence |
| Rank-based | Select by rank order, not raw fitness | Robust to fitness scale changes; loses magnitude info |
| Roulette (fitness-proportional) | Probability ∝ fitness | Fails when fitness can be negative or near-constant |
| Elitism | Copy top N unchanged into next gen | Always include; prevents regression |

Bounding on parent re-draw (cap the number of attempts to get distinct parents) prevents hangs on tiny populations.

### Crossover

For real-valued genomes:

```python
def blend_crossover(parent_a, parent_b, alpha=0.5):
    """BLX-α: each gene uniformly sampled from [min−αd, max+αd]."""
    d = np.abs(parent_a - parent_b)
    low = np.minimum(parent_a, parent_b) - alpha * d
    high = np.maximum(parent_a, parent_b) + alpha * d
    child = np.random.default_rng().uniform(low, high)
    return child

def single_point_crossover(parent_a, parent_b):
    point = np.random.randint(1, len(parent_a))
    return np.concatenate([parent_a[:point], parent_b[point:]])
```

For structured genomes, crossover must respect the structure. In NEAT, crossover matches genes by innovation number — homologous genes cross over, disjoint/excess genes come from the fitter parent.

### Mutation

```python
def gaussian_mutation(genome, rate=0.1, sigma=0.1, rng=None):
    rng = rng or np.random.default_rng()
    mask = rng.random(len(genome)) < rate
    genome = genome.copy()
    genome[mask] += rng.normal(0, sigma, size=mask.sum())
    return genome

def adaptive_mutation(genome, fitness, population_fitness, rate_base=0.1, sigma_base=0.1):
    """Lower mutation rate for high-fitness individuals (exploit), raise for low (explore)."""
    # Simple heuristic: scale by how far below the population mean this genome is
    ...
```

Mutation rate and sigma are themselves hyperparameters. Adaptive schemes (raise mutation when fitness stagnates, lower when improving) help on hard problems.

### The main loop

```python
def evolve(pop_size, genome_size, generations, evaluate, mutate, crossover, select):
    population = [random_genome() for _ in range(pop_size)]
    for gen in range(generations):
        fitnesses = evaluate(population)           # parallel, returns per-agent scalar
        next_gen = []
        # Elites
        elite_idx = np.argsort(fitnesses)[-ELITE_COUNT:]
        for i in elite_idx:
            next_gen.append(population[i].copy())
        # Fill rest
        while len(next_gen) < pop_size:
            parent_a = select(population, fitnesses)
            parent_b = select(population, fitnesses)
            child = crossover(parent_a, parent_b)
            child = mutate(child)
            next_gen.append(child)
        population = next_gen
        log_generation(gen, fitnesses)
    return population
```

### Common GA defects

| Symptom | Likely cause | Fix |
|---|---|---|
| Fitness flatlines at zero | Evaluation silently failing (exception swallowed, default 0) | Let evaluation raise; don't flatten failures into zero |
| All agents play identically | Genome not actually read in evaluation (random policy independent of weights) | Verify the phenotype reads the genome on every decision |
| Selection operates on wrong data | Weight accessor returns the Torch network (huge) instead of the genome (small) | Ensure selection/crossover/mutation all use the same genome representation |
| No convergence after many generations | Mutation too high, selection too weak, or fitness signal too noisy | Lower mutation, increase tournament size, reduce evaluation noise via shared RNG |
| Population collapses to one clone | Elitism too aggressive or mutation too low | Reduce elite count, raise mutation rate |
| Fitness improves then regresses | Overfitting to a fixed evaluation set | Rotate evaluation opponents/seeds across generations; use Elo for cross-gen comparison |

## Tournament Evaluation

When fitness comes from matches, not a scalar environment reward, use tournaments.

### ELO

```python
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_a, rating_b, actual_a, k=32):
    expected_a = expected_score(rating_a, rating_b)
    rating_a += k * (actual_a - expected_a)
    rating_b -= k * (actual_a - expected_a)
    return rating_a, rating_b
```

- `actual_a` is 1 for a win, 0.5 for a draw, 0 for a loss.
- K controls how fast ratings move. K=32 is common for games; lower for stable ratings, higher for quickly-converging populations.
- Track Elo *per agent* and use the best Elo across generations as the champion metric — raw fitness isn't comparable between generations if the field changes.

### Swiss pairing

For large populations, Swiss is much cheaper than round-robin:

```python
def swiss_pairings(elo_ratings, rounds=None):
    """Generate pairings for ceil(log2 N) rounds; pair similar-rated agents."""
    n = len(elo_ratings)
    if rounds is None:
        rounds = int(np.ceil(np.log2(n)))
    paired = set()
    pairings = []
    for _ in range(rounds):
        sorted_agents = sorted(range(n), key=lambda i: elo_ratings[i], reverse=True)
        round_pairings = []
        for i in range(0, n - 1, 2):
            if sorted_agents[i] not in paired and sorted_agents[i+1] not in paired:
                round_pairings.append((sorted_agents[i], sorted_agents[i+1]))
                paired.add(sorted_agents[i])
                paired.add(sorted_agents[i+1])
        pairings.append(round_pairings)
    return pairings
```

Each agent plays ~log₂(N) matches instead of N−1. Byes score as half points. Dispatch pairings across workers.

### Formats

| Format | Matches | Use when |
|---|---|---|
| Round-robin | N(N−1)/2 | Small populations, need exhaustive comparison |
| Swiss | N·log₂(N) | Large populations, ranking matters more than exhaustive data |
| Single elimination | N−1 | Fast champion discovery, not for fitness estimation |
| Double elimination | ~2N | More robust champion, still cheap |
| League | configurable subset | You want specific opponents matched |

### Head-to-head fairness

- Record winner/loser explicitly from the match result — don't infer sides from who played where.
- If the environment is asymmetric (player 1 vs player 2 has different starting conditions), mirror the arena and let each genome play both sides, then average.
- Side-symmetric policies (one genome plays either side with the arena mirrored) halve the evaluation cost and let you compare agents directly.

## NEAT (NeuroEvolution of Augmenting Topologies)

NEAT evolves both weights and topology. It starts minimally and adds complexity only when it helps.

### Genome structure

A NEAT genome is a list of connection genes, each with:
- **in_node**, **out_node** — which nodes it connects
- **weight** — the connection weight
- **enabled** — whether it's active (can be disabled by mutation)
- **innovation_number** — a global ID that identifies this gene across the population

Node genes list the neurons (with activation function). The network is built by walking the enabled connections.

### Innovation numbering

Innovation numbers let crossover match homologous genes. When a new mutation (add node, add connection) occurs, it gets the next global innovation number. Two genomes with the same innovation number have the same historical origin — those genes are homologous and can be crossed over meaningfully.

Implementation: maintain a global `innovation_table` mapping (from_node, to_node, activation) → next_innovation_number. When a new connection is added, check the table; if it's there, reuse the number; if not, allocate a new one. In a single-process run, this is just a counter. In a parallel run, you need a shared counter or a deterministic scheme.

### Speciation

Novel structures are vulnerable — a new topology with random weights will likely be worse than a refined old one, and crossover with the mainstream will destroy it. NEAT protects novelty via speciation:

1. Compute compatibility distance between every pair of genomes (disjoint genes + excess genes + weight differences, weighted by coefficients).
2. Cluster into species by distance threshold.
3. Each species gets a fitness share based on its performance relative to its own members, not the whole population.
4. New species get a fitness boost (survival threshold) to protect them through the initial bad phase.

The distance formula:

```python
def compatibility_distance(genome_a, genome_b, c1=1.0, c2=1.0, c3=0.5):
    excess_and_disjoint = (genome_a.disjoint + genome_b.disjoint)  # simplified
    avg_weight_diff = np.mean(np.abs(genome_a.weights - genome_b.weights))
    return c1 * excess_and_disjoint / max(len(genome_a), len(genome_b)) + c3 * avg_weight_diff
```

Tune c1, c2, c3 on your problem — they control how aggressively you split species.

### NEAT mutation operators

| Operator | Effect | Typical rate |
|---|---|---|
| Add connection | Adds a new link between existing nodes (no cycles) | 0.1–0.3 per genome per generation |
| Add node | Splits an existing connection, inserts a node with one enabled in/out | 0.05–0.15 |
| Mutate weight | Gaussian perturbation of existing weights | 0.9–1.0 (most genomes get this) |
| Enable/disable connection | Toggles a gene | 0.1–0.2 |

### NEAT crossover

For two genomes with different innovation numbers:
- Matching genes (same innovation number): pick randomly from either parent, or from the fitter parent with some bias.
- Disjoint/excess genes: come from the fitter parent (the one with more genes, typically).

This preserves the historical structure that speciation depends on.

### When NEAT helps vs hurts

NEAT shines when:
- The optimal architecture is unknown and you want the algorithm to find it.
- The problem benefits from increasing complexity over time.
- You have a small population and want to preserve diversity.

NEAT adds overhead:
- Compatibility distance computation is O(N²·G) where G is genome size — expensive on large populations.
- Speciation adds bookkeeping.
- For fixed-architecture problems, a simple GA over weights is usually faster per unit of progress.

## Parallel Evaluation Patterns

### Worker pool

```python
from multiprocessing import Pool, cpu_count

def evaluate_population(population, evaluate_single, n_workers=None):
    n_workers = n_workers or cpu_count() - 1
    with Pool(n_workers) as pool:
        # Tag each task so results reassemble correctly
        tasks = [(i, agent) for i, agent in enumerate(population)]
        results = pool.starmap(evaluate_worker, tasks, chunksize=1)
    results.sort(key=lambda r: r[0])  # reassemble by index
    return [r[1] for r in results]

def evaluate_worker(idx, agent):
    try:
        fitness = evaluate_single(agent)
        return (idx, fitness)
    except Exception as e:
        log.error(f"Evaluation failed for agent {idx}: {e}")
        return (idx, -np.inf)  # or skip
```

### Common random numbers

```python
def evaluate_generation(population, opponent_decks, seeds, evaluate_match):
    """All agents in a generation see the same opponents and seeds."""
    fitnesses = np.zeros(len(population))
    for i, agent in enumerate(population):
        for opp_deck, seed in zip(opponent_decks, seeds):
            fitnesses[i] += evaluate_match(agent, opp_deck, seed=seed)
    return fitnesses / len(opponent_decks)
```

Seed advances per generation, not per agent. This ensures fitness differences reflect genome differences, not match luck.

### GPU evaluation

For large populations of neural networks, batch inference on GPU can be much faster than per-agent CPU inference. The pattern:

1. Stack all genomes into a batched input tensor.
2. Run one forward pass per match state (or batch the match states).
3. Collect actions and continue the simulation.

Watch for: GPU memory limits with large populations, and the overhead of transferring state to/from GPU per tick. If the simulation is CPU-bound (game logic, physics), GPU evaluation of the policy may not help much — profile first.

## Model Export

When an evolved model needs to run outside the training pipeline:

### NumPy genome → file

```python
np.save("agent_genome.npy", genome)           # raw weights
# or with metadata
export = {"genome": genome.tolist(), "version": 1, "config": config_dict}
with open("agent.json", "w") as f:
    json.dump(export, f)
```

### PyTorch network export

```python
# TorchScript
traced = torch.jit.trace(network, example_input)
traced.save("agent.pt")

# ONNX
torch.onnx.export(network, example_input, "agent.onnx",
                  input_names=["input"], output_names=["output"])
```

### Loading with validation

When loading an exported model, validate the shape/size before trusting it. A genome file that's the wrong length is a common corruption mode. Reject by shape, not by trusting the file.

## Tracking & Diagnostics

Evolution is a long-running process — you need to see what's happening inside, not just the final result.

### What to log per generation

- Mean/median/min/max fitness
- Best agent's genome (or a hash of it) and its fitness
- Population diversity (mean pairwise distance, or number of species)
- Evaluation time per generation
- Any alerts (fitness plateau, population collapse, NaN genomes)

### Convergence detection

```python
def has_converged(fitness_history, window=20, threshold=1e-4):
    if len(fitness_history) < window:
        return False
    recent = fitness_history[-window:]
    return np.std(recent) < threshold
```

Plateau detection is a trigger for: raising mutation, switching opponents, or stopping early.

### Diversity monitoring

A population that converges to a single genome too fast is stuck. Track:
- Number of species (NEAT)
- Mean pairwise distance in weight space
- Unique genome count (hash the genomes)

If diversity drops to near-zero and fitness is flat, the population is broadcasting on a single frequency — increase mutation or inject fresh genomes.

## Multi-Objective Evolution

When you have two or more conflicting objectives (e.g., win rate vs. match length, thrust vs. efficiency in KSP):

### Pareto front

An individual A dominates B if A is at least as good on all objectives and strictly better on at least one. The Pareto front is the set of non-dominated individuals. Selection can favor individuals on the front or use a scalarization.

### Scalarization approaches

- **Weighted sum**: `fitness = w1 * obj1 + w2 * obj2`. Simple but can't represent non-convex fronts.
- **Rank-based**: rank each objective separately, sum ranks. Handles trade-offs better than raw values.
- **Epsilon-constraint**: optimize one objective, constrain the other(s) to be above a threshold.

### NSGA-II style

Rank individuals by non-dominated front number (front 0 = Pareto front), then by crowding distance within a front (prefer diverse solutions). Select by rank first, then crowding. This is the most common multi-objective EA and is worth implementing if you have 2–3 objectives.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Silent evaluation failure → zero fitness | Population doesn't learn; all fitnesses look equal | Don't swallow exceptions; let failures propagate or log explicitly |
| Fitness not comparable across generations | Best fitness rises then falls; can't tell if it's improving | Use shared RNG, common opponents, or ELO |
| Genome and phenotype out of sync | Mutations don't change behavior | Verify the phenotype reads the genome on every decision; test a known mutation |
| Overfitting to evaluation opponents | Agent beats the field but loses to anything new | Rotate opponents, use diverse evaluation, hold out a test set of opponents |
| Population collapses to one genome | Diversity → 0, fitness flatlines | Increase mutation, reduce elitism, inject fresh genomes, monitor diversity |
| NEAT speciation threshold wrong | One species dominates (too large) or everyone is its own species (too small) | Tune c1/c2/c3; monitor species count per generation |
| Parallel evaluation nondeterministic | Same genome scores differently run to run | Seed each worker deterministically; log seeds |
| Export/load shape mismatch | Loaded model crashes or behaves wrong | Validate shape/size on load; reject by length |
| Tournament pairing bias | Some agents get easier opponents | Use Swiss or randomized pairings; track opponent strength |

## Production Patterns from Evolved-Agent Systems

Patterns that show up repeatedly in working evolutionary ML systems — drawn from CR-pipeline (Clash Royale GA with Swiss/ELO tournaments, 279-test suite, parallel sim) and KSP_pipeline (NEAT neuroevolution for Kerbal Space Program, multi-objective GA, GPU net, orbit sim).

### Tournament evaluation at scale

For a population of N agents where fitness comes from matches:

**Swiss pairing (default for large populations):**
- ⌈log₂ N⌉ rounds; each agent plays ~log₂(N) matches instead of N−1.
- Pair agents with similar current scores — strong vs strong, weak vs weak.
- Byes (odd number of agents) score as half points.
- Dispatch pairings across a worker pool (`ParallelRunner.run_pairings` pattern).
- At N=200: 800 matchups vs 19,900 for round-robin — the practical difference between "runs in an hour" and "doesn't run."

**ELO tracking:**
- K=32 is the working default for game-like domains (adjust lower for stable long-running populations, higher for fast-converging ones).
- Track ELO per agent and use *best ELO across generations* as the champion metric, not raw fitness — raw fitness isn't comparable between generations when the field changes.
- `update_elo(rating_a, rating_b, actual_a, k=32)` where `actual_a` is 1/0.5/0 for win/draw/loss.
- Compute expected from ratings (`1 / (1 + 10^((rb-ra)/400))`), derive actual from the *result*, not from the ratings.

**Hall of fame:**
- Carry past champions across generations as non-reproducing benchmarks.
- Without a hall of fame, the population can drift/cycle without anything actually improving — fitness rises while the champion can't beat its own ancestor.
- Track best agent by ELO (comparable across generations) not fitness (not comparable between fields).

### Common random numbers

Fitness differences should reflect genome differences, not match luck:

- All agents in a generation share the same seeds and opponent deck sequence.
- Seed advances *per generation*, not per agent — so the population is never graded repeatedly on one fixed set of games.
- Opponent AIs seed once at engine init, not per tick — reseeding per tick makes fitness irreproducible.
- Each match advances the seed: `seed + i * 1000` so N matches in a worker measure N distinct things, not N copies of one.

### Multi-objective GA

When you have conflicting objectives (e.g., thrust vs. efficiency in KSP, win rate vs. match length in CR):

**NSGA-II style ranking (the common approach for 2–3 objectives):**
- Rank individuals by non-dominated front number (front 0 = Pareto front — the set of individuals not dominated by any other).
- Within a front, rank by crowding distance — prefer diverse solutions along the front, not clustered in one corner.
- Select by rank first, then crowding distance.

**Scalarization alternatives:**
- Weighted sum (`w1*obj1 + w2*obj2`) — simple, but can't represent non-convex fronts.
- Rank-based sum — rank each objective separately, sum ranks. Handles trade-offs better than raw values when objectives have different scales.
- Epsilon-constraint — optimize one objective, constrain the others to be above a threshold. Useful when one objective is clearly primary.

The KSP_pipeline pattern: multi-objective GA where the Pareto front is tracked per generation and the "best" agent is chosen by a decision on the trade-off (e.g., maximize delta-v efficiency subject to a minimum thrust), not by a single scalar.

### GPU batch evaluation

For large populations of neural networks, batch inference on GPU can be much faster than per-agent CPU inference:

- Stack all genomes into a batched input tensor.
- Run one forward pass per match state (or batch the match states).
- Collect actions and continue the simulation on CPU.

Watch for:
- GPU memory limits with large populations — profile before scaling.
- Transfer overhead: moving state to/from GPU per tick can dominate if the simulation is CPU-bound (game logic, physics). GPU evaluation of the policy helps most when the policy is the bottleneck.
- The KSP_pipeline `gpu_net.py` pattern: a Torch network that lives on GPU, with the simulation loop feeding it batched states and collecting batched outputs.

### NEAT topology evolution

The KSP_pipeline `neat.py` pattern (simplified NEAT — evolves weights AND topology):

**Genome structure:**
- Connection genes: (in_node, out_node, weight, enabled, innovation_number).
- Node genes: (node_id, activation_function).
- Network built by walking enabled connections from inputs through hidden to outputs.

**Innovation numbering:**
- Global counter mapping (from_node, to_node, activation) → innovation number.
- New mutations (add node, add connection) get the next number.
- Two genomes sharing an innovation number have a common historical origin — those genes are homologous and can be crossed over meaningfully.
- In single-process runs, this is just a counter. In parallel runs, you need a shared counter or deterministic allocation.

**Speciation:**
- Compatibility distance: disjoint genes + excess genes + weight differences, weighted by coefficients (c1, c2, c3).
- Cluster into species by distance threshold.
- Each species gets fitness relative to its own members, not the whole population.
- New species get a survival boost to protect them through the initial bad phase.
- c1/c2/c3 tuned per problem — they control how aggressively you split species. Too aggressive = everyone is their own species. Too lenient = one species dominates.

**Mutation operators (rates are starting points, tune per problem):**
- Add connection: 0.1–0.3 per genome per generation.
- Add node: 0.05–0.15 (splits an existing connection, inserts a node).
- Mutate weight: 0.9–1.0 (most genomes get this every generation).
- Enable/disable connection: 0.1–0.2.

**When NEAT vs simple GA:**
- NEAT: optimal architecture unknown, problem benefits from increasing complexity over time, small population where you want to preserve diversity.
- Simple GA over weights: fixed architecture is fine, you want speed per unit of progress, population is large enough to explore without speciation.
- NEAT overhead: O(N²·G) compatibility distance computation (N = population, G = genome size). For large populations, this dominates. Profile before committing to NEAT on a big population.

### Population management and checkpointing

**Population initialization:**
- Don't construct the full Torch network at init — build lazily. CR-pipeline went from ~0.87s/20 agents to ~0.02s by storing only the policy genome at init and building the Torch network on demand.
- For a NumPy policy, the genome *is* the population state — store the flat vector, not a wrapper object.

**Checkpoint/resume:**
- Save the population (genomes + fitnesses + metadata), the generation number, and the RNG state.
- Resume: load the population, restore the RNG, continue from the saved generation.
- If resuming mid-generation, decide whether to re-run the incomplete generation or skip to the next. CR-pipeline seeds chosen agents intact and fills remaining slots with mutated copies — that's one reconciliation strategy.
- Validate on load: check genome sizes, population count, generation number. A corrupted checkpoint that loads silently is worse than a failed load.

### Experiment tracking for evolutionary runs

What to log per generation (beyond the obvious mean/std/best):

- Best agent genome hash (not the full genome — a hash is stable and compact) + its fitness/ELO.
- Population diversity metrics: number of species (NEAT), mean pairwise distance, unique genome count.
- Evaluation time per generation (catch slowdown bugs early).
- Alerts: fitness plateau (std over a window below threshold), population collapse (diversity → 0), NaN genomes.
- Run-level metadata: seed, config hash, start time, end time, total evaluation count.

For run comparison: store enough that you can compare two runs later. A run directory with per-generation metrics files, the final population, and a run-level metadata file is the minimal shape. CR-pipeline's `experiment_tracking.py` pattern: runs discoverable by directory, comparable by fitness curves, with a report generator that produces a summary.

## Neural Architecture Search (NAS) with Evolution

When you want to evolve not just weights but the network structure itself — the CR-pipeline pattern.

**Separate the evolved policy from the architecture under evolution.** CR-pipeline keeps the 2,311-parameter NumPy policy as the primary representation; the Torch architectures (CNN+LSTM, MLP, ResNet, Transformer, GRU, and variants — 9 of them in `architecture.py`) are for NAS, export, and ensembling. The genome is the thing selection operates on; the architecture is a separate axis you can search over when you want to.

**Architecture representation for evolution:**
- Encode the architecture as part of the genome or as a parallel structure: layer types, filter sizes, number of layers, attention heads, activation functions, connectivity.
- Keep it tractable — the space is combinatorially large. Constrain the search to a sensible subset (e.g., choose from 9 known-good architectures rather than inventing arbitrary topologies).
- The KSP_pipeline `neat.py` approach is the more general case: evolve topology from scratch (add node, add connection), starting minimal and growing. The CR-pipeline approach is the pragmatic case: pick from a curated set and evolve weights on top.

**When to use NAS vs fixed architecture:**
- Fixed architecture + evolved weights: you know the architecture is approximately right, you want the best weights. Fast, predictable.
- NAS: you don't know the architecture, the problem is novel, or you suspect the architecture is the bottleneck. Expensive, but can find structures a human wouldn't pick.
- The CR-pipeline hybrid: keep the lightweight NumPy policy for the main evolution loop (fast evaluation), use the Torch architectures for export, ensembling, and when you want to try a different inductive bias.

## Ensemble Methods for Evolved Populations

When you have a population of good agents and want to combine them — the CR-pipeline `ensemble.py` pattern.

**Weight averaging (performance-weighted):**
- Combine the genomes of top agents, weighted by their fitness or ELO.
- Simple, often effective, preserves the population's learned structure.
- The combination weight optimization: find the weights that maximize tournament fitness of the ensemble, not just the average of individual fitnesses.

**Geometric mean:**
- For genomes that are positive-valued or can be made so, the geometric mean is more robust to outliers than the arithmetic mean.
- Use when individual genomes vary widely and you want a conservative combination.

**Stacking with a meta-learner:**
- Train a small model to combine the outputs of the top agents.
- More powerful than simple averaging, but adds a layer that can overfit.
- Useful when the agents have complementary strengths (one is good on one opponent type, another on another) and you want the combination to exploit that.

**When ensembling helps:**
- The population has converged to several distinct good solutions (diversity survived), and combining them is better than any one.
- You want a more robust agent for deployment (less sensitive to a particular opponent or condition).
- You're exporting a model and want the best single artifact — the ensemble is often more robust than the best single genome.

**When ensembling doesn't help:**
- The population has collapsed to one good genome (no diversity to combine).
- The agents are all correlated (they learned the same thing), so averaging doesn't add information.
- The evaluation cost of the ensemble is prohibitive (you have to run N agents per decision).

## Curriculum Learning in Evolution

When the problem is too hard to learn from scratch — start easy, ramp up.

**Phase-based curriculum:**
- Phase 1: easy opponents, simple conditions, small population.
- Phase 2: harder opponents, more variation, larger population (seeded from Phase 1's best).
- Phase 3: full difficulty, full population, the real evaluation conditions.

**Automatic phase transitions (CR-pipeline's convergence detection):**
- Detect when the population has converged in the current phase (fitness plateau, diversity drop).
- Transition to the next phase automatically — don't wait for a human to decide.
- Log the transition (what phase, why, what the population looked like).

**Seeding across phases:**
- Phase N's best agents seed Phase N+1 — don't start from random.
- Carry the hall of fame across phases so the new phase is benchmarked against the old.

**Pitfalls:**
- Curriculum that's too easy → the population learns the easy problem and can't generalize to the hard one.
- Curriculum that's too coarse → the jump between phases is too big, the population collapses.
- Phase transition that loses diversity → the new phase starts from a narrow base. Carry diversity metrics across the transition.

## Alerting and Monitoring in Long-Running Evolution

Evolution runs can take hours or days. You need to know if something goes wrong before the run finishes.

**Alerts to implement (CR-pipeline's `alerting/` pattern):**
- **Convergence alert:** fitness plateau detected (std over a window below threshold). Not necessarily a failure — it's a signal to raise mutation, switch opponents, or check if the run is done.
- **Bottleneck alert:** evaluation is slower than expected (time per generation rising). Could be a resource issue (CPU/GPU saturation), a sim bug (matches getting longer), or a population that's grown too large.
- **Fitness milestone alert:** best fitness crosses a threshold. Useful for long runs where you want to know when the agent reaches a certain capability.
- **Early-stop alert:** the run has hit a stopping condition (max generations, fitness target, convergence). Triggers clean shutdown and final reporting.
- **GPU error alert:** CUDA OOM, device loss, or other GPU failures. These are common in long GPU runs and should alert immediately, not after the run crashes.

**Channels:**
- Console (always on — the run's stdout is the default channel).
- File (log file that persists beyond the run, useful for post-mortem).
- Optional: webhook, email, desktop notification (for runs that are being watched).

**What alerts should NOT do:**
- Stop the run automatically (an alert is information, not a decision — the run might be supposed to plateau).
- Spam (coalesce alerts, don't fire one per generation when the condition persists).

## Resource Monitoring

Watch the resources the run is using, not just the ML metrics.

**CPU:** utilization across workers, load average. If CPU is saturated and evaluation is slow, the bottleneck is compute, not algorithm.
**GPU:** memory usage, utilization, temperature. OOM is the common failure mode — monitor memory and leave headroom.
**Memory:** system memory, swap. A population that grows too large or a data leak in the evaluation can exhaust memory silently.
**Disk:** space for checkpoints, logs, run artifacts. A long run that fills the disk crashes late.

**Bottleneck detection (CR-pipeline's `monitoring/` pattern):**
- Collect metrics over time (CPU, GPU, memory, evaluation time per generation).
- Detect when a resource is the bottleneck (sustained high utilization + slow evaluation).
- Surface the bottleneck: "evaluation is slow because GPU memory is saturated" is actionable; "evaluation is slow" is not.

## Stats and Significance for Evolutionary Runs

Don't just report mean fitness — report whether differences are real.

**Confidence intervals on fitness:**
- Mean fitness with a confidence interval (bootstrap or standard error) tells you the precision of the estimate.
- If two runs' confidence intervals overlap heavily, the difference may not be meaningful.

**Statistical significance testing (CR-pipeline's dashboard pattern):**
- When comparing two populations, two runs, or two configurations, test whether the difference is significant.
- For tournament results: a paired test (same opponents, same seeds) is more powerful than an unpaired one.
- Report the p-value or confidence interval alongside the raw difference.

**Effect size:**
- A statistically significant difference can be tiny in practice. Report effect size (how big is the difference, in meaningful units) alongside significance.
- "Run B is significantly better than Run A (p<0.05) but by 0.01 fitness units" — significant but not useful.
- "Run B is 0.3 fitness units better than Run A with non-overlapping confidence intervals" — significant and meaningful.

## Run Comparison and Reporting

When you have multiple runs and want to compare them — the CR-pipeline `runs_manager.py` + `experiment_tracking.py` pattern.

**What to compare:**
- Fitness curves (mean, best, over generations) — the primary comparison.
- Final population metrics (best fitness, diversity, ELO distribution).
- Tournament results between champions of different runs.
- Evaluation time and resource usage (was one run more efficient?).

**Run discovery:**
- Runs stored in a directory tree, each run a subdirectory with its metrics, checkpoints, and metadata.
- A runs manager that discovers runs, reads their metadata, and presents them for comparison.
- Metadata: run ID, seed, config, start/end time, generations, final fitness, status (completed, stopped, failed).

**Report generation:**
- A report subcommand or function that produces a summary of one or more runs.
- Human-readable (console or markdown) and/or machine-readable (JSON).
- Include: what ran, what the result was, whether it was significant, what to do next.

## Defect Taxonomy for Evolutionary Systems

Categories of defects that show up repeatedly, with the test or observation that catches them:

**Evaluation defects (the fitness signal is wrong):**
- Evaluation silently fails and returns a default (zero, negative infinity) — fitness signal is noise.
- Evaluation ignores the genome (returns a random or constant value) — selection can't work.
- Evaluation is non-deterministic in a way that adds noise larger than the signal — selection sorts noise.
- Evaluation is too expensive to run properly (truncated, sampled badly) — fitness is approximate in a biased way.

**Selection defects (the selection pressure is wrong):**
- Selection operates on the wrong data (the Torch network instead of the genome) — selection is on something that doesn't affect behavior.
- Selection pressure too weak (small tournament, too much randomness) — no convergence.
- Selection pressure too strong (large tournament, too few elites) — premature convergence, loss of diversity.
- Elitism wrong (elites not preserved, or too many elites) — best solutions lost or population can't explore.

**Crossover/mutation defects (the variation is wrong):**
- Crossover produces invalid genomes (wrong size, out of bounds, broken structure) — offspring don't work.
- Mutation rate too high (genome destroyed faster than selection can improve it) — no convergence.
- Mutation rate too low (no exploration) — population stuck on a local optimum.
- Mutation operator wrong for the representation (e.g., Gaussian mutation on a discrete genome) — variation doesn't make sense.

**Evaluation design defects (the fitness landscape is wrong):**
- Fitness is noisy (match luck, environment randomness) — selection sorts noise.
- Fitness is not comparable across generations (field changes, opponents change, seeds change) — can't tell if the population is improving.
- Fitness is overfit to the evaluation conditions (agent learns the evaluation, not the problem) — looks good in training, bad in deployment.
- Fitness has the wrong shape (flat regions, discontinuities, local optima that trap the population) — evolution can't navigate.

**Deployment defects (the exported model is wrong):**
- Export doesn't include the architecture or config — loaded model can't run or runs wrong.
- Export/load changes the model (rounding, ordering, precision) — loaded model behaves differently.
- Exported model not validated against the training-time model — you don't know if the export is correct.

The fix for each category is different. Diagnose which category the defect is in before trying to fix it — "fitness isn't improving" could be an evaluation defect, a selection defect, a variation defect, or a fitness landscape defect, and the fix for each is different.

- [ ] Evaluation doesn't silently swallow failures (fitness signal is real)
- [ ] Fitness is comparable across generations (shared RNG / common opponents / ELO)
- [ ] A known mutation produces a known behavioral change (genome → phenotype integrity test)
- [ ] Baseline agents (random, heuristic, hand-crafted) are evaluated alongside the population
- [ ] Diversity is monitored and doesn't collapse prematurely
- [ ] Best agent is re-evaluated on held-out opponents/conditions
- [ ] Exported model loads and matches the training-time behavior
- [ ] Run is reproducible from the seed and config (same seed → same result)
