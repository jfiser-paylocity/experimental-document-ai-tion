---
name: find-feature-android
description: Given a module name, locate its root path in the Android project.
---

# Goal

Given a module name (e.g. "Punch"), locate its root path in the Android project.

# Step-by-step Instructions

## Step 1 — List available modules

List the `<project_path>/PaylocityNG/` directory. Android feature modules are Gradle modules as direct children (e.g. `punch/`).

## Step 2 — Match the module name

Match the user-provided name against directory names (case-insensitive, also check hyphenated variants like `punch-v2`).

**Exact command:**

```sh
find <project_path>/PaylocityNG -maxdepth 1 -type d -iname "<moduleName>*"
```

List results for the user to pick if more than one match.

## Step 3 — Confirm the match

Verify that `src/main/java/` or `src/main/kotlin/` exists inside the matched module directory.

**Source root convention:**

```
<match>/src/main/java/com/paylocity/pcty/<module>/
```

or

```
<match>/src/main/kotlin/com/paylocity/pcty/<module>/
```

## Handling edge cases

### No match found

If no exact match is found, try a fuzzy match:

```sh
find <project_path>/PaylocityNG -maxdepth 1 -type d -iname "*<moduleName>*"
```

If a single close match exists (e.g. "Punch" → `punch-v2`), use it.

If no match at all, report "Module not found" and list all available modules:

```sh
ls <project_path>/PaylocityNG/
```

### Multiple matches found

List all matches and ask the user to clarify which one to use.
