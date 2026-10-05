---
name: pinned-data-contracts
description: "Frozen releases, contract versions, checked pins."
version: 1.0.0
author: Hermes Agent (from the knowledge vault's pinned-releases-and-data-contracts page; AsteroidCatalog, economicspace, spacecost, 2026-10)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [data-contract, reproducibility, releases, pinning, manifest, sha256, provenance, bit-identity]
    related_skills: [bit-identity-float-pipelines, one-authority-per-fact, ci-gate-design, space-data-pipelines, economicspace-pipeline, verification-culture]
---

# Pinned releases and data contracts

## What This Skill Does

Describes the discipline that lets repos that feed each other (a data builder, a cost library, a model) depend on each other without drifting: **publish frozen artifacts, stamp them with a contract version, pin consumers to a tag, and check the pins mechanically.** The examples are the owner's space-economics stack (AsteroidCatalog to economicspace, spacecost to economicspace).

## When to Use

- A repo consumes another repo's data or library and must stay reproducible
- Publishing a dataset release, or bumping its schema
- Comparing two builds, or repinning a consumer
- Not for float hashing mechanics (`bit-identity-float-pipelines`), pipeline implementation (`space-data-pipelines`), or the economicspace model itself (`economicspace-pipeline`)

## The pieces

- **Frozen releases**: one build per tag (for example `data-YYYY-MM-DD`), never rebuilt under the same tag, with a `manifest.json` of sha256s. The reason: a live source changes daily, so only a frozen release is the same bytes on every host.
- **Publish gates**: the release command refuses on missing sources, shrinkage, duplicate IDs or physically impossible values; a failed gate publishes nothing.
- **Data contract = a `pipeline_version`**: consumers refuse an artifact whose contract is not theirs, and verify every byte against its sha256 before replacing anything on disk.
- **Bit-identity where it can be promised, tolerance where it cannot**: promise byte-identical tables on every platform; promise a summary with `exp()` in it only to a few ULP, checked on a recorded reference platform in CI. Two builds on the same library versions eleven hours apart differed in the last bit on 74,414 diameters and 124,109 masses, so compare releases **by value with a tolerance, never by hash**.
- **Pins in code and prose, checked**: a pin typed in seven places needs a check that fails when they disagree (and a check that covers the prose copies).
- **Deterministic analyses**: pin the catalog tag in config, sha256-check inputs, seed one RNG, and compare a full CI run to a committed summary.

## Rules that fall out

- A repin is a deliberate, recorded act; it moves every downstream number as a rebuild would.
- **Compare contracts, not package versions.** A bump can add a column and move no value; a number can move with only a contract bump upstream. Still repin deliberately, because daily upstream changes ride along in any new release.
- **A switch that turns a new model off should reproduce the old one to the bit**, proved on hashed cells before measuring the change.
- **A consumer measures a release before pinning it; a producer fixes a contract with a new tag.** A consumer that valued a new minor release found a column 6 to 12% too poor; the producer published a patch contract the same day, kept the bad tag published as superseded, and added a test that fails on the old split.
- **Replay inputs to isolate a model change**: rebuild a price table by replaying recorded quotes with no network, so an A/B runs on identical inputs.
- When comparing two builds, strip **both** provenance columns (`pipeline_version` and `catalog_date`), or midnight between runs looks like a defect.

## Procedure

1. Producer: freeze the release, write the manifest, gate the publish, stamp the contract.
2. Consumer: pin the tag in one place and have a check read every copy of the pin (`current`, `behind`, `split`, `missing`).
3. On a new release, measure the effect on downstream numbers first, then repin and record it.
4. Compare builds by value with a tolerance and without provenance columns.
5. Make CI check out the dependency at the pinned tag, so the pin check actually runs.

## Pitfalls

- Rebuilding under an existing tag.
- Comparing releases by hash when hosts differ in the last bit.
- A pin that exists in code but not in prose, or the reverse.
- Treating a version bump as a number change, or the reverse.

## Verification

- [ ] Releases are immutable and carry a sha256 manifest and a contract version
- [ ] Every copy of a pin agrees and a check proves it
- [ ] Repin was measured and recorded before it landed
- [ ] Release comparisons use tolerance and ignore provenance columns
