---
name: find-feature-ios
description: Given a module name, locate its root path in the iOS project.
---

# Goal

Given a module name (e.g. "Punch"), locate its root path in the iOS project.

# Step-by-step Instructions

## Step 1 — List available packages

List the `<project_path>/Packages/` directory. iOS feature modules are Swift packages under `Packages/` named `Pcty<Feature>` (e.g. `PctyPunch`).

## Step 2 — Match the module name

Match the user-provided name against package directory names (case-insensitive prefix match on `Pcty<Name>`).

**Exact command:**

```sh
find <project_path>/Packages -maxdepth 1 -type d -iname "Pcty<ModuleName>"
```

If exactly one result, that is the module root.

## Step 3 — Confirm the match

Verify that `Sources/Pcty<Name>/` exists inside the matched package directory. The source root is:

```
<match>/Sources/Pcty<ModuleName>/
```

## Handling edge cases

### No match found

If no exact match is found, try a fuzzy match:

```sh
find <project_path>/Packages -maxdepth 1 -type d -iname "Pcty*<ModuleName>*"
```

If a single close match exists (e.g. "Rewards and Recognition" → `PctyRewardsAndRecognition`), use it.

If no match at all, report "Module not found" and list all available packages:

```sh
ls <project_path>/Packages/
```

### Multiple matches found

List all matches and ask the user to clarify which one to use.
