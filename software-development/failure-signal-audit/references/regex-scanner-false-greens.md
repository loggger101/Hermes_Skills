---
description: "Case study: regex security/lint scanners that report score 100 or PASS on real defects (Terraform scanner, flag auditors); checklist for trusting a scanner's green"
source_repo: alirezarezvani/claude-skills (MIT) - engineering/terraform-patterns and engineering/feature-flags-architect
tested_version: "tf_security_scanner.py, flag_debt_scanner.py, kill_switch_audit.py run on Python 3.14.6 / Windows against planted fixtures; no terraform or tofu binary was installed, so no .tf file was planned or applied"
verified_date: "2026-10-05"
---

# Regex scanners that report green on real defects

`failure-signal-audit` looks for swallowed errors and false greens. Pattern-matching scanners are a prime source: they print
a clean score, exit 0, and the number gets quoted as evidence. `terraform-patterns/scripts/tf_security_scanner.py` (a
"score out of 100" Terraform security scanner) and two feature-flag auditors were run against planted defects. Each row
is one fixture, one run.

## Terraform scanner (`tf_security_scanner.py`)

| Planted defect | Scanner output |
|---|---|
| `aws_db_instance` with `password = "hunter2hunter2"` inside `modules/x/main.tf` | score **100**, no findings: only the top directory is read (`os.listdir`, non-recursive) |
| Two S3 buckets, an encryption-configuration resource for bucket `a` only | score **100**: one repo-wide `any encryption resource exists` test, bucket names never matched |
| One unencrypted bucket, and the text `server_side_encryption_configuration` appears only in a comment in another file | score **100** (files are joined, then substring-matched) |
| Ingress `from_port=0 to_port=0 protocol="-1"` open to `0.0.0.0/0` (all traffic) | score **100**: the all-ports rule needs `to_port >= 65535` |
| `aws_vpc_security_group_ingress_rule` (SSH) and `aws_security_group_rule` (RDP) open to `0.0.0.0/0` | score **100**: only inline `ingress {}` inside `aws_security_group` is parsed |
| IAM `Action = ["*"]`, `Resource = ["*"]` (list form) and `aws_iam_policy_document` with `actions = ["*"]` | score **100**: only the `Action = "*"` string form matches |
| Two security groups both open on port 22 | **one** finding (dedupe key is the rule text, which has no resource name) |
| IAM statement `Effect = "Deny"`, `Action = "*"`, `Resource = "*"` | score 35, three findings: a false positive, because Effect is ignored |
| `password = "${var.db_password}"` | critical finding (false positive: the value is an interpolation, not a literal) |
| `variable "token_ttl_seconds"` (a number) | medium finding "appears to be a secret" (name substring) |
| `variable "db_password" { type = string }` on one line | no finding (block regex needs a newline before `}`) |
| Any run with critical findings | exit code **0** (the process only prints), so it cannot gate CI as written |

Real coverage is therefore: inline `ingress {}` blocks of literal CIDRs, a handful of literal secrets, and string-form IAM
wildcards, in the top-level directory only. For anything that gates a merge use a parser-based tool (for example
Checkov, tfsec/Trivy, or `terraform validate` plus a policy engine) and treat this scanner as a quick smell test. None of
those tools was run here.

## Feature-flag scripts

`flag_debt_scanner.py` never dates a flag added by editing an existing file, and exempts old flags that are used widely;
`kill_switch_audit.py` passes `Owner: TBD / Kill switch: none` and passes a sentence that merely contains the words.
Details and fixes are in `devops/feature-flag-lifecycle/references/feature-flag-lifecycle.md`.

## Checklist before trusting a scanner's green

1. **Plant a defect per rule** in the shape the rule claims to cover, then in two or three realistic variants (list form,
   other resource type, subdirectory, other file, single-line block). A scanner that finds only the exact string from its own
   demo has the coverage of its demo.
2. **Check scope**: does it recurse? Does it read every file type it should? Are files joined so one file's text answers
   another's question?
3. **Check the exit code** on a failing fixture, and that the exit code is what CI reads.
4. **Check for global tests that should be per-object** (one encryption resource silencing every bucket).
5. **Check what "present" means**: a field passes if the *word* appears, or if the *value* is real?
6. **Report the blind spots** next to the score: "no findings in the files the scanner reads" is a different claim from
   "no issues".
