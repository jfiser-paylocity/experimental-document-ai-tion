# Shared Rules for All Agents

These rules apply to all documentation agents and subagents in this project.

## Exhaustive Reading

Read every relevant file completely. Do not skip or summarize source code — all fields and types must be extracted.

## Scope

Stay scoped to the provided package/module. Do not include information from other parts of the codebase outside the specified scope.

## Search Settings

Always use `maxResults: 500` on every grep/search call. The default limit silently truncates results.

## File Reading Strategy

For files with many matches (10+), read the entire file in large chunks (100+ lines) rather than small snippets.

## Platform Detection

Determine the platform from the project path or structure. Use the platform to select the correct skill file.

## Source of Truth

The client implementation is the single source of truth. Generate documentation from source code, not from existing docs.

## Test Exclusion

Exclude all test files and test directories from analysis.

## Output Convention

All documentation output uses platform-agnostic terminology (not Swift/Kotlin-specific types).
