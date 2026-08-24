---
name: test-infra-ml
description: "Testing ML systems: sims, EAs, tournaments, checkpoints."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, ML, simulation, evolutionary-algorithms, tournaments, checkpoints, deterministic, pytest]
    category: software-development
    related_skills: [python-craft, test-driven-development, evolutionary-ml]

---

# Testing Infrastructure for ML Systems

Guide for testing ML systems — simulation engines, evolutionary algorithms, tournament evaluation, checkpoints/resume, and the patterns that catch real defects without making tests useless or slow.

## When to Use

- Building or maintaining a simulation engine (game sim, physics sim, environment) and wanting to catch correctness bugs
- Building an evolutionary algorithm and wanting to verify selection, crossover, mutation, and the main loop actually work
- Building tournament evaluation and wanting to verify ELO, pairings, and result attribution
- Building checkpoint/resume and wanting to verify resume produces the same state
- Any ML system where correctness matters and the "right answer" is computable in a test

**Don't use** exhaustive property-based testing for everything — it's expensive and can be brittle. Use targeted tests for the things that have known-correct answers (simulation invariants, tournament math, genome integrity) and behavioral tests for the things that don't (does the evolved agent actually play better?).

## Testing Simulation Engines

Simulation engines are worth testing heavily because bugs there are silent — the sim runs, produces numbers, and the numbers are wrong in a way that's hard to spot from the outside.

### Invariants

Test the invariants that should hold for every valid simulation state:

```python
def test_energy_conserved_in_two_body(sim):
    """Specific orbital energy should be constant in two-body motion."""
    initial_energy = sim.specific_orbital_energy()
    for _ in range(100):
        sim.tick()
    assert np.isclose(sim.specific_orbital_energy(), initial_energy, atol=1e-9)
```

```python
def test_angular_momentum_conserved(sim):
    """Specific angular momentum should be constant without external forces."""
    initial_h = sim.specific_angular_momentum()
    for _ in range(100):
        sim.tick()
    assert np.allclose(sim.specific_angular_momentum(), initial_h, atol=1e-9)
```

Invariants catch entire classes of bugs — if energy isn't conserved, something in the integration or force computation is wrong.

### Deterministic replay

A simulation that's seeded should produce the same output for the same seed:

```python
def test_deterministic(sim_factory):
    sim_a = sim_factory(seed=42)
    sim_b = sim_factory(seed=42)
    state_a = []
    state_b = []
    for _ in range(50):
        state_a.append(sim_a.tick())
        state_b.append(sim_b.tick())
    assert state_a == state_b
```

This catches RNG usage bugs (seeding per tick instead of per sim, shared global RNG, etc.) and non-deterministic behavior (thread scheduling affecting results, unordered iteration over sets).

### Round-trip: state → elements → state

For orbital mechanics or any system with a state↔elements conversion:

```python
def test_state_elements_roundtrip(state, mu):
    elements = state_to_elements(state, mu)
    reconstructed = elements_to_state(elements, mu)
    assert np.allclose(reconstructed.position, state.position, atol=1e-9)
    assert np.allclose(reconstructed.velocity, state.velocity, atol=1e-9)
```

Round-trip tests catch errors in both directions at once. If either conversion is wrong, the round-trip fails.

### Known-answer tests

For computations with known answers:

```python
def test_hohmann_delta_v():
    """Hohmann transfer from 7000km to 10000km around Earth."""
    mu = 398600.4418  # km^3/s^2
    r1, r2 = 7000.0, 10000.0
    dv1, dv2, total = hohmann_delta_v(mu, r1, r2)
    # Known values (compute once, verify by hand or reference)
    assert np.isclose(dv1, 0.225, atol=1e-3)
    assert np.isclose(dv2, 0.175, atol=1e-3)
```

Known-answer tests are the most valuable when the computation is hard to verify by inspection — delta-v, orbital element conversions, ELO updates. Compute the expected value once (by hand, from a reference, or from a trusted implementation) and lock it in.

### Edge cases

Test the boundaries:
- Circular orbit (e=0): do the conversions handle the degeneracy?
- Escape trajectory (e>=1): does the code handle hyperbolic orbits?
- Zero velocity, zero distance: does it crash or handle gracefully?
- Large numbers, small numbers: does precision hold?

### Simulation correctness defects to catch

From CR-pipeline's history (these are real defects that were caught and fixed):

| Defect | Test that catches it |
|---|---|
| King tower not flagged as building → king attacks twice per tick | Test: king attacks at most once per tick; test: building units don't move |
| King placed at wrong row → instant king kill | Test: match doesn't end in <5% of runs by instant king kill; test: king is behind princess towers |
| Crowns only on king kill → draws at time limit | Test: matches can end with crowns from princess towers; test: overtime triggers on tied regulation |
| _cycle_hand replaces all slots every 3rd tick | Test: hand has stable card indices across ticks; test: only played card cycles |
| Spells restricted to caster's half | Test: spell can reach enemy tower across the river |
| apply_status compares enum to int → no effect | Test: status effects apply (stun/slow change unit behavior) |
| Dead units not removed | Test: dead units removed from unit list after death; test: unit list length doesn't grow without bound |
| Attack interval computed at 60Hz not sim Hz | Test: attack interval matches sim TICKS_PER_SECOND; test: unit attacks at expected frequency |
| Opponent reseeded per tick | Test: same seed → same match outcome; test: fitness is reproducible across runs |
| Every match in worker same seed | Test: N matches in a worker have N distinct seeds |
| Head-to-head ELO attribution inverted half the time | Test: winner's ELO increases, loser's decreases; test: ELO change is symmetric |

The pattern: each defect has a test that would have caught it. When you fix a defect, add the test. When you write a simulation, anticipate the categories of bugs (wrong state mutation, wrong condition, wrong rate, inverted logic, ignored edge case) and write tests for them.

## Testing Evolutionary Algorithms

### Genome integrity

```python
def test_mutation_changes_genome():
    genome = random_genome(seed=42)
    mutated = gaussian_mutation(genome, rate=1.0, sigma=0.1, rng=np.random.default_rng(123))
    assert not np.array_equal(genome, mutated)  # rate=1.0 mutates every gene

def test_crossover_produces_valid_genome():
    parent_a = random_genome(seed=1)
    parent_b = random_genome(seed=2)
    child = blend_crossover(parent_a, parent_b)
    assert len(child) == len(parent_a)
    assert np.all(child >= np.minimum(parent_a, parent_b) - 0.5 * np.abs(parent_a - parent_b))
    assert np.all(child <= np.maximum(parent_a, parent_b) + 0.5 * np.abs(parent_a - parent_b))
```

### Selection correctness

```python
def test_tournament_select_returns_valid_member():
    population = [random_genome(seed=i) for i in range(10)]
    fitnesses = np.array([i for i in range(10)])  # 9 is best
    selected = tournament_select(population, fitnesses, k=3, random_state=42)
    assert selected in population

def test_elite_preserved():
    population = [random_genome(seed=i) for i in range(10)]
    fitnesses = np.array([i for i in range(10)])
    next_gen = evolve_one_generation(population, fitnesses, elite_count=2)
    # Top 2 by fitness should be in next_gen unchanged
    best_idx = np.argsort(fitnesses)[-2:]
    for i in best_idx:
        assert population[i] in next_gen  # or array_equal
```

### Evolution loop sanity

```python
def test_population_size_preserved():
    population = [random_genome(seed=i) for i in range(50)]
    fitnesses = evaluate(population)
    next_gen = evolve_one_generation(population, fitnesses, pop_size=50)
    assert len(next_gen) == 50

def test_generation_advances():
    pop, gen = initialize()
    for _ in range(5):
        pop, gen = step(pop, gen)
    assert gen == 5
```

### Fitness signal test

The most important test for an EA: does fitness actually reflect the genome?

```python
def test_fitness_differs_between_genomes():
    genome_a = random_genome(seed=1)
    genome_b = random_genome(seed=2)
    fitness_a = evaluate_single(genome_a, seed=42)
    fitness_b = evaluate_single(genome_b, seed=42)
    # They should differ (unless the problem is degenerate)
    assert not np.isclose(fitness_a, fitness_b) or evaluate_single(genome_a, seed=43) != evaluate_single(genome_b, seed=43)
```

If all genomes get the same fitness, selection can't work. This test catches the defect where evaluation ignores the genome (returns a constant or a random value independent of the genome).

```python
def test_known_mutation_produces_known_behavior_change():
    """A specific mutation should produce a specific, observable change."""
    genome = make_test_genome()
    mutated = apply_known_mutation(genome, mutation_index=10, new_value=1.0)
    assert mutated[10] == 1.0
    # And the behavior should change in a predictable way
    action_before = evaluate_policy(genome, fixed_state, fixed_seed)
    action_after = evaluate_policy(mutated, fixed_state, fixed_seed)
    assert action_before != action_after  # the mutation changed something observable
```

This is the genome→phenome integrity test. If a known mutation doesn't change behavior, the phenotype isn't reading the genome correctly.

## Testing Tournament Evaluation

### ELO correctness

```python
def test_elo_expected_score():
    assert expected_score(1500, 1500) == 0.5
    assert expected_score(1600, 1500) > 0.5
    assert expected_score(1500, 1600) < 0.5
    assert abs(expected_score(1500, 1500) - 0.5) < 1e-9

def test_elo_update_symmetric():
    ra, rb = 1500.0, 1500.0
    ra2, rb2 = update_elo(ra, rb, 1.0, k=32)  # A wins
    assert ra2 > ra
    assert rb2 < rb
    assert abs(ra2 - 1500) == abs(rb2 - 1500)  # symmetric

def test_elo_update_reflects_result():
    """ELO should move based on the result, not pre-match ratings."""
    ra, rb = 1500.0, 1500.0
    _, rb_win = update_elo(ra, rb, 0.0, k=32)  # A loses → B wins
    assert rb_win > rb
    # Reversing the result should reverse the change
    ra2, rb2 = update_elo(ra, rb, 1.0, k=32)
    assert ra2 == rb_win  # A winning gives A what B got from winning
```

### Tournament format tests

```python
def test_swiss_pairings_cover_all_agents():
    ratings = list(range(10))
    pairings = swiss_pairings(ratings)
    all_paired = set()
    for round_pairings in pairings:
        for a, b in round_pairings:
            all_paired.add(a)
            all_paired.add(b)
    assert all_paired == set(range(10))

def test_round_robin_has_expected_matches(n=5):
    matches = generate_round_robin(n)
    assert len(matches) == n * (n - 1) // 2
    # Each pair appears exactly once
    pairs = set(tuple(sorted(m)) for m in matches)
    assert len(pairs) == len(matches)
```

### Result attribution

```python
def test_winner_recorded_correctly():
    """Winner/loser recorded from result, not inferred from sides."""
    result = play_match(agent_a, agent_b, seed=42)
    assert result.winner == result.winning_agent
    assert result.loser == result.losing_agent
    # Swap sides and play again — winner should still be recorded from outcome
    result2 = play_match(agent_a, agent_b, seed=42, swap_sides=True)
    assert result2.winner in (agent_a, agent_b)
    # ELO update uses the recorded winner, not the side
    updated_a, updated_b = update_elo_from_result(agent_a.rating, agent_b.rating, result)
    assert updated_a > agent_a.rating if result.winner == agent_a else updated_a <= agent_a.rating
```

The head-to-head attribution bug (CR-pipeline: "Head-to-head computed both agents as player side then recorded swapped block as if sides changed → ELO win attribution inverted half the time") is caught by a test that verifies the winner is recorded from the match outcome, not inferred from which side they played.

## Testing Checkpoints and Resume

### Checkpoint contents

```python
def test_checkpoint_contains_required_fields(ckpt):
    assert "population" in ckpt
    assert "generation" in ckpt
    assert "seed" in ckpt
    assert "fitness" in ckpt  # or per-agent fitnesses
    assert "config" in ckpt
```

### Resume produces same state

```python
def test_resume_reproduces_state(save_dir, tmp_path):
    # Run 5 generations, checkpoint
    run_training(generations=5, save_dir=save_dir, seed=42)
    ckpt = load_checkpoint(save_dir / "latest.pt")

    # Resume from checkpoint and run 3 more generations
    run_training(resume=save_dir / "latest.pt", generations=3, save_dir=tmp_path / "resumed")

    # The resumed run's state at generation 8 should match a fresh run to generation 8
    fresh_dir = tmp_path / "fresh"
    run_training(generations=8, save_dir=fresh_dir, seed=42)
    fresh_ckpt = load_checkpoint(fresh_dir / "latest.pt")

    assert ckpt["generation"] == 5  # checkpoint is at gen 5
    assert fresh_ckpt["generation"] == 8
    # Population at gen 8 should match (same seed, same code)
    resumed_ckpt = load_checkpoint(tmp_path / "resumed" / "latest.pt")
    assert np.allclose(resumed_ckpt["population"], fresh_ckpt["population"])
```

### Resume edge cases

- Resume from a checkpoint with a different config: should fail or clearly warn (config mismatch).
- Resume from a corrupted checkpoint: should fail cleanly (validation on load), not silently produce wrong results.
- Resume with a partial checkpoint (missing field): should fail, not fill in defaults that change the result.

## Testing at Scale

### What to keep fast

- Unit tests for individual functions (selection, crossover, mutation, ELO, state conversions) — fast, run on every change.
- Invariant tests for the simulation — fast, run on every change.
- Known-answer tests — fast, run on every change.

### What can be slower

- Full integration tests that run a generation or a match — mark them, run them in CI but not on every save.
- Behavioral tests that evolve a population and check improvement — slow, run occasionally or in CI.

### What to mock

- External services (CRM, APIs) — mock in tests, don't call real services.
- Expensive simulation steps — mock or use a tiny/simplified sim for tests.
- Large datasets — use a small sample for tests, not the full dataset.

### Deterministic test configs

For tests that run the actual pipeline (training, simulation, evolution):
- Small population, few generations, fixed seed.
- Cheap evaluation (tiny sim, mock env, or simplified opponent).
- Assert on structure and invariants, not on exact fitness values that might drift with code changes.

## Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| No invariant tests on simulation | Wrong sim logic goes undetected | Add energy/angular momentum/round-trip invariant tests |
| Non-deterministic tests | Flaky CI, tests pass/fail randomly | Seed everything; avoid shared global RNG; test determinism |
| Fitness test that always passes | Can't detect when evaluation ignores genome | Test that different genomes produce different fitness; test known mutation → known behavior change |
| ELO test that doesn't check result dependency | ELO update ignores actual result | Test that ELO change reflects the result argument, not just ratings |
| Tournament test that doesn't verify attribution | Winner/loser inference bugs undetected | Test that winner is recorded from outcome, not side |
| Checkpoint test that only checks it loads | Corrupted checkpoint loads silently | Validate checkpoint contents; test resume reproduces state |
| Full pipeline test runs every commit | CI is slow, tests get skipped | Mark slow tests; use small deterministic configs; mock expensive steps |
| Testing only the happy path | Defects on edge cases undetected | Test circular orbits, escape trajectories, zero velocity, large/small numbers |
| No test added when fixing a defect | Same defect reintroduced later | Add the test that would have caught the defect; regression test |

## Testing the Data Pipeline

When the ML system includes a data pipeline (loading, transforming, augmenting, feeding data to the model) — test the data path, not just the model.

**Data loading tests:**
- Loading the dataset produces the expected shape (rows, columns, types).
- Loading the dataset catches corrupt files (malformed CSV, truncated Parquet, wrong schema) and fails clearly.
- Loading a dataset with missing values handles them correctly (NaN, imputation, filtering — whatever the pipeline does).
- Loading a dataset with the wrong schema fails clearly (schema validation on load).

**Data transformation tests:**
- Each transformation step produces the expected output given a known input (round-trip or known-answer).
- Transformations are deterministic (same input → same output) unless they're intentionally stochastic (augmentation) — in which case seed them for tests.
- transformations compose correctly (step A then step B produces the expected result, not step B acting on the wrong representation).

**Data augmentation tests (CR-pipeline's `augmentation.py` pattern):**
- Augmentation produces valid outputs (augmented deck compositions are valid decks, augmented opponent strategies are valid strategies, augmented game conditions are valid conditions).
- Augmentation doesn't produce degenerate outputs (a deck with no cards, a strategy that's all zeros, a condition that's impossible).
- Augmentation is seeded for tests (deterministic augmentation for a known seed, so the test can assert on the exact output).
- Augmentation is configurable (the test can turn specific augmentations on/off and verify the effect).

**Data feeding tests:**
- The data loader feeds the model the expected input shape (the model's input tensor has the right dimensions).
- Batches are constructed correctly (correct batch size, correct shuffling, correct padding if variable-length).
- The data loader handles the end of the dataset correctly (last batch smaller than batch size, or dropped, or padded — whatever the design is).
- Epoch boundaries are correct (the data loader goes through the dataset once per epoch, not twice or half).

**Data integrity tests:**
- The dataset hasn't drifted (the distribution of key columns is within expected bounds — catch data drift early).
- The dataset is what you think it is (checksums on the source data, version stamps on the processed data).
- Cumulative runs don't double-count (for pipelines that accumulate across runs — the high-water mark or manifest is correct).

## Testing Checkpoint/Restore for Data Pipelines

When the data pipeline has checkpoint/restore (resuming a long data run, re-running from an intermediate) — test it.

**Checkpoint contents:**
- The checkpoint contains everything needed to resume: the current position in the data, the accumulated state, the RNG state, the config.
- The checkpoint is valid on load (schema check, completeness check).

**Resume produces the same result:**
- Run to completion, save checkpoint at step N, resume from checkpoint, run to completion — the final output matches a run that went N steps without checkpointing.
- This catches checkpoint bugs (state not fully captured, RNG not restored, resume skipping or duplicating work).

**Resume edge cases:**
- Resume from a corrupted checkpoint fails clearly (validation on load), not silently producing wrong results.
- Resume from a partial checkpoint (missing fields) fails, not fills in defaults that change the result.
- Resume with a config mismatch (the checkpoint was produced with a different config than the resume) fails or warns clearly.

## Property-Based Testing for ML Systems

When you want to test invariants across a wide range of inputs, not just hand-picked test cases — property-based testing (Hypothesis for Python) is the tool.

**What to property-test:**
- State↔elements conversions: for any valid state, the round-trip should recover the original state (within tolerance). Property-test across a wide range of states (random states that satisfy the validity constraints).
- Orbital mechanics functions: for any valid input (valid orbit, valid transfer), the output should satisfy invariants (energy conservation, correct delta-v sign, valid resulting orbit).
- Evolution operators: for any valid genome, mutation should produce a valid genome (same size, in bounds, valid structure). For any valid pair of genomes, crossover should produce a valid child.
- Data transformations: for any valid input, the transformation should produce a valid output (correct shape, correct types, no NaN unless expected).

**How to property-test:**
```python
from hypothesis import given, strategies as st

@given(st.floats(-1e7, 1e7), st.floats(-1e7, 1e7), st.floats(-1e7, 1e7))
def test_state_elements_roundtrip_property(rx, ry, rz):
    # Build a valid state from random position/velocity
    state = make_valid_state(rx, ry, rz, ...)
    if not state.is_valid():
        return  # skip invalid states
    elements = state_to_elements(state, mu)
    reconstructed = elements_to_state(elements, mu)
    assert np.allclose(reconstructed.position, state.position, atol=1e-6)
    assert np.allclose(reconstructed.velocity, state.velocity, atol=1e-6)
```

**What NOT to property-test:**
- Things with no clear invariant (the agent's policy output for a random state — there's no "correct" answer to test against).
- Things that are too expensive to run many times (a full evolution run, a full training run — property-based testing runs the test many times, so expensive tests are prohibitive).
- Things that depend on external state (the current time, a network call, a file on disk — property-based testing assumes the test is self-contained).

**Shrinking:**
- When a property test fails, Hypothesis shrinks the failing input to a minimal failing case. This is valuable — it turns a random failing state into a small, understandable one.
- Make sure your test strategies generate shrinkable inputs (floats, integers, lists, structs — Hypothesis handles these; custom strategies may need shrinking support).

## Regression Testing for ML Defects

When you fix a defect, add a regression test that would have caught it. The pattern from CR-pipeline's fix history.

**Regression test structure:**
- Name the defect clearly (the test name or docstring says what defect it's guarding against).
- Reproduce the conditions that triggered the defect (the specific input, config, or sequence that caused it).
- Assert that the defect doesn't recur (the fix is in place, the behavior is correct).

**Examples from CR-pipeline's history:**
- "King tower not flagged as building → king attacks twice per tick" → regression test: king attacks at most once per tick; building units don't move.
- "Crowns only awarded for a king kill → draws at time limit" → regression test: matches can end with crowns from princess towers; overtime triggers on tied regulation.
- "Head-to-head ELO attribution inverted half the time" → regression test: winner's ELO increases, loser's decreases; ELO change is symmetric.

**Regression test maintenance:**
- Keep regression tests as part of the regular test suite (not a separate "historical" suite that gets neglected).
- If a regression test becomes obsolete (the defect can't recur because the code has changed fundamentally), remove it — but only if you're sure.
- If a regression test is slow, make it fast (mock the expensive part, reduce the scope) or mark it as slow and run it in CI.

## Test Organization for ML Projects

How to organize tests so they're useful and not a burden.

**By layer:**
- **Unit tests:** individual functions (selection, crossover, mutation, ELO, state conversions, data transforms). Fast, run on every change.
- **Integration tests:** a step of the pipeline (one generation, one match, one data load+transform+feed). Slower, run in CI.
- **End-to-end tests:** the full pipeline (full training run, full tournament, full data pipeline). Slowest, run occasionally or on demand.

**By domain:**
- **Simulation tests:** invariants, determinism, round-trip, known-answer, edge cases, defect regression.
- **Evolution tests:** genome integrity, selection correctness, fitness signal, loop sanity, defect regression.
- **Tournament tests:** ELO correctness, format coverage, result attribution, defect regression.
- **Data pipeline tests:** loading, transformation, augmentation, feeding, integrity, checkpoint/resume.
- **Deployment tests:** export/load validation, behavioral validation, format compatibility.

**By speed:**
- **Fast tests:** run on every save/commit. Unit tests, invariant tests, known-answer tests.
- **Slow tests:** run in CI, not on every save. Integration tests, some regression tests.
- **Slowest tests:** run on demand or on a schedule. Full end-to-end runs, large-scale behavioral tests.
- Mark tests by speed (pytest markers: `@pytest.mark.slow`, `@pytest.mark.e2e`) so you can run subsets.

**Test data:**
- Small, deterministic test datasets (not the full production dataset). A 10-row CSV for testing the data loader, not the 1.5M-row one.
- Synthetic test data for the sim (known orbits, known states, known transfers) — not recording real trajectories and testing against them (real trajectories have noise and don't have known-correct answers).
- For evolution tests: small populations, few generations, cheap evaluation (mock env, tiny sim, simplified opponent).

**Test fixtures:**
- Reusable fixtures for common test setup (a sim factory, a population factory, a dataset loader, a tournament runner).
- Fixtures that produce deterministic outputs (seeded, small, cheap) so tests are repeatable.
- Fixtures that are scoped appropriately (session-scoped for expensive setup that's shared across tests, function-scoped for setup that should be fresh per test).

- [ ] Simulation has invariant tests (energy, angular momentum, round-trip, deterministic replay)
- [ ] Known-answer tests for computations with verifiable expected values (delta-v, ELO, element conversions)
- [ ] Edge cases tested (circular, hyperbolic, zero, boundary values)
- [ ] EA has genome integrity tests (mutation changes genome, crossover produces valid genome, selection returns valid members)
- [ ] EA has fitness signal test (different genomes → different fitness; known mutation → known behavior change)
- [ ] Tournament has ELO correctness tests (expected score, symmetric update, result-dependent update)
- [ ] Tournament has format tests (pairings cover all agents, round-robin match count correct)
- [ ] Tournament has result attribution test (winner recorded from outcome, not side)
- [ ] Checkpoint test validates contents and resume reproduces state
- [ ] Defect-fixing commits include regression tests
- [ ] Slow tests marked and run in CI, not on every save
- [ ] Tests use deterministic configs and mock external services
