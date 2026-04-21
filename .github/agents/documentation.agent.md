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

# Steps

## Step 1: Find and validate the target module
- Find the project path first. If multiple matches are found, ask the user to clarify.
- Use the `find-feature-<platform>` skill to locate requested modules in the project.
- If project or module cannot be found, inform the user and end the process early.

## Step 2: Fetch existing documentation

Fetch any existing documentation for the target module. This will be passed to subagents so they can compare and produce a changelog.

### From Confluence

1. Use the Confluence page title map (below) to resolve page titles for the target module.
2. Discover existing child pages:
   ```sh
   npx confluence children <parentPageId> --recursive --format json --show-id
   ```
3. For each leaf page, fetch its content:
   ```sh
   npx confluence read <pageId> --format markdown
   ```

### Fallback: local docs

If confluence-cli is not configured or the page doesn't exist, read from local `docs/<module>/<type>/<platform>.md` files instead.

Store the fetched content to pass to subagents in Step 3.

## Step 3: Run subagents to gather documentation data

Run the following subagents in parallel to gather different aspects of the documentation. Each agent should return its output as a markdown string.

When invoking each subagent, include the fetched existing documentation (from Step 2) as part of the prompt message, clearly delimited:

```
## Existing Documentation
<content of the existing doc, or "No existing documentation found.">
```

- `api-communication.agent` — generates comprehensive API documentation for the specified package/module. Pass the existing API doc for the detected platform.
- `datadog-logs.agent` — generates comprehensive Datadog log points documentation for the specified module. Pass the existing logs doc for the detected platform.

## Step 4: Output

Save subagent results to the `docs` directory in Markdown format, organized by module, documentation type and platform (e.g. `docs/punch/api/android.md`, `docs/punch/logs/android.md`).

Write subagent results directly — just overwrite them, DO NOT perform any validation/diff checking/patching. The comparison and validation is the subagent's responsibility.

### Upload to Confluence

Use the `confluence-cli` tool to upload final documentation to Confluence. If the documentation page already exists, update it. If it does not exist, create a new page under the appropriate parent page.

Follow the hierarchy and structure of the local `docs` directory when creating/updating pages in Confluence. DO NOT skip any levels.

#### Exact Confluence commands

- **Read a page:**
  ```sh
  npx confluence read <pageId> --format markdown
  ```
- **List children:**
  ```sh
  npx confluence children <parentPageId> --recursive --format json --show-id
  ```
- **Create a child page:**
  ```sh
  npx confluence create-child "<title>" <parentPageId> --format markdown --file <path>
  ```
- **Update a page:**
  ```sh
  npx confluence update <pageId> --format markdown --file <path>
  ```

#### Confluence page title map

To avoid collisions in confluence page titles, use the following naming convention derived from the local doc path:

| Local Doc Path                      | Confluence Page Title                              |
|-------------------------------------|----------------------------------------------------|
| `docs/<module>`                     | Document-AI-tion - \<Module\>                      |
| `docs/<module>/api`                 | Document-AI-tion - \<Module\> - API                |
| `docs/<module>/logs`                | Document-AI-tion - \<Module\> - Datadog            |
| `docs/<module>/api/<platform>.md`   | Document-AI-tion - \<Module\> - API - \<Platform\> |
| `docs/<module>/logs/<platform>.md`  | Document-AI-tion - \<Module\> - Datadog - \<Platform\> |

Where `<Module>` and `<Platform>` are title-cased (e.g. `tasks` → `Tasks`, `android` → `Android`).