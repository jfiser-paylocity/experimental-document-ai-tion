---
description: Generate documentation for the project. (master agent)
argument-hint: Generate a documentation for Punch module in the mobile-next-gen-ios project.
agents:
  - api-communication
  - datadog-logs
tools:
  - agent
  - edit/createDirectory
  - edit/createFile
  - edit/editFiles
  - execute/getTerminalOutput
  - execute/runInTerminal
  - execute/sendToTerminal
  - read/readFile
  - search/codebase
  - search/fileSearch
  - search/listDirectory
  - search/searchResults
model: GPT-5.4 mini
---

Orchestrate the documentation generation process from the source code by running dedicated agents. Do not generate documentation directly in this agent. Instead, delegate to subagents that specialize in different aspects of the documentation (e.g. API communication, architecture overview, data models, etc.). Each subagent should return its output as a markdown string, which you will compile into a final documents hierarchy.

# Input
- User MUST provide a specific package/module identification (for example by name).

# Requirements
- Subagents MUST ignore any existing documentation and only focus on the source code. The client implementation is the single source of truth.
- Subagents MUST read every relevant file completely. They MUST NOT skip or summarize source code — all fields and types must be extracted.
- Subagents MUST be scoped to the provided package/module. They MUST NOT include information from other parts of the codebase that are outside the specified scope.

# Steps

## Step 1: Find and validate the target module
- Find the project path first. If multiple matches are found, ask the user to clarify.
- Search the project for the provided module name. If multiple matches are found, ask the user to clarify.
- If project or module cannot be found, inform the user and end the process early.

## Step 2: Run subagents to gather documentation data

Run the following subagents in parallel to gather different aspects of the documentation. Each agent should return its output as a markdown string.
- `api-communication.agent` - generates comprehensive API documentation for the specified package/module.
- `datadog-logs.agent` - generates comprehensive Datadog log points documentation for the specified module.

# Output
Store all documentation in Markdown format in the `docs` directory in the root, organized by module, documentation type and platform (e.g. `docs/punch/api/android.md`, `docs/punch/logs/android.md`).

If the documentation already exists, update it with new information instead of overwriting. Only focus on actual changes since the last update, do not regenerate the entire document or change wording/blank spaces.

## Upload to Confluence

Use the `confluence-cli` tool to first read an existing Confluence tree/pages for the target module. If the documentation page already exists, update it with the new content. If it does not exist, create a new page under the appropriate parent page.

Follow the hierarchy and structure of the local `docs` directory when creating/updating pages in Confluence.
### Confluence page title map

To avoid collisions in confluence page titles, use the following mapping from local documentation paths to Confluence page titles:

| Local Doc Path           | Confluence Page Title                |
|--------------------------|--------------------------------------|
| `docs/punch`             | Document-AI-tion - Punch             |
| `docs/punch/api`         | Document-AI-tion - Punch - API       |
| `docs/punch/logs`        | Document-AI-tion - Punch - Datadog   |
| `docs/punch/api/ios.md`  | Document-AI-tion - Punch - API - iOS (or Android) |