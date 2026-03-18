# Review Documentation

Review all documentation across the core repo and service repos for misalignment with the actual codebase.

## Metadata

```yaml
triggers:
  - "review documentation"
  - "review docs"
  - "check documentation alignment"
  - "audit docs"
  - "documentation review"
  - "docs out of date"
```

## When to Use

Use this skill after changes have been made to services, architecture, or patterns, to identify where documentation has drifted from reality.

## Input / Output

**Input:** No input required. The skill scans the core repo and all service repos under `services/`.
**Output:** A structured report with two sections — **CRITICAL** and **SUGGESTIONS** — each finding including a short description and a complexity rating.

## Persona

You are a documentation auditor. Your job is to find misalignment between documentation and reality — not to fix it, improve style, or evaluate test coverage. You surface findings clearly and concisely. You do not rewrite, patch, or suggest code changes.

## Instructions

### Step 1: Collect all documentation files.

Scan for `.md` files in these locations:
- Core repo root (e.g. `AGENTS.md`, `ARCHITECTURE.md`, `STYLES.md`, `CLAUDE.md`, `README.md`)
- Each service directory under `services/*/` (root-level `.md` files)
- `.agents/` directories at the root of the core repo and each service repo — read rules and skills files but do not recurse deeper than one level into subdirectories

### Step 2: Prioritise the critical files.

Read these files first and in full before any others, as they are the most likely source of destructive misalignment:
- `AGENTS.md`
- `ARCHITECTURE.md`
- `STYLES.md` (if present)

### Step 3: Cross-reference documentation against observable reality.

For each documentation file, check:
- **Directory and path references** — do named directories, files, and services actually exist?
- **Service names and ports** — do they match `compose.yml` and `service-compose/`?
- **Technology claims** — do stated languages, frameworks, and tools match what is in the service repos (e.g. `package.json`, `pyproject.toml`, `requirements.txt`)?
- **Pattern descriptions** — do described patterns (e.g. auth, routing, data flow) match actual service code at a structural level?
- **Table entries in AGENTS.md** — do all listed rules, skills, and service `.agents/` directories exist on disk?

Do not evaluate whether every rule is being followed in every file. Look only for structural misalignment: broken references, missing artefacts, and contradictions between documents.

### Step 4: Check `.agents/` directories for glaring misalignment.

For each `.agents/rules/` and `.agents/skills/` directory in the core repo and each service:
- Confirm the files listed in `AGENTS.md` exist on disk
- Check rule files for references to directories, file patterns, or named conventions — verify these exist
- Note any rules that describe patterns clearly absent from the repo (e.g. a rule about a test directory that does not exist)

Do not evaluate whether code follows the rules. Only flag rules that reference things that do not exist or contradict other rules.

### Step 5: Classify each finding.

Assign every finding to exactly one category:

**CRITICAL** — misalignment that will compound over time and actively mislead future development. Examples:
- A path or service name in a core doc that does not exist
- A technology or framework claim that is wrong
- An AGENTS.md table entry pointing to a missing file
- Two documents that contradict each other on a structural fact

**SUGGESTION** — misalignment that is stale, incomplete, or inconsistent but not immediately destructive. Examples:
- A section that is vague or likely outdated but not factually wrong
- A missing section that would be useful but its absence does not mislead
- A `.agents/` rule that references a pattern that has changed but still roughly applies

### Step 6: Assign a complexity rating to each finding.

Rate each finding on two dimensions:

- **Spot difficulty** — how hard is it to identify exactly what needs changing? (`easy` / `moderate` / `hard`)
- **Change scope** — how many files or locations need to be updated? (`single file` / `a few files` / `wide-reaching`)

Format: `Spot: easy | Scope: single file`

### Step 7: Write the report.

Output the report in this structure:

```
## CRITICAL

### [Short title]
**File:** `path/to/file.md`
**Finding:** [One or two sentences describing the misalignment.]
**Complexity:** Spot: [easy/moderate/hard] | Scope: [single file / a few files / wide-reaching]

---

## SUGGESTIONS

### [Short title]
**File:** `path/to/file.md`
**Finding:** [One or two sentences describing the misalignment.]
**Complexity:** Spot: [easy/moderate/hard] | Scope: [single file / a few files / wide-reaching]
```

If no issues are found in a category, write: `None found.`

Do not include fixes, rewrites, or code suggestions in the report.
