---
name: confluence-cli
description: Use confluence-cli to read, create and update Confluence pages from the terminal.
argument-hint: <pageId, URL, search query, or task description>
---

# confluence-cli Skill

A CLI tool for Atlassian Confluence. Lets you read, create and update pages from the terminal or from an agent.

## Constraints

You are only allowed to create/edit child pages of the root page with ID 3112108456. This is to ensure all content created by the agent is organized under a single parent page. Do not create or edit pages outside of this subtree. Do not edit the given root page.

You are NOT allowed to use any other command than what is listed here.

Always print out list of pages that were created or edited, along with their URLs.

## Installation validation

```sh
confluence --version   # verify install
```

## Configuration

Environment variables are the preferred way for configuration:

| Variable | Description | Example |
|---|---|---|
| `CONFLUENCE_DOMAIN` | Your Confluence hostname | `company.atlassian.net` |
| `CONFLUENCE_API_PATH` | REST API base path | `/wiki/rest/api` (Cloud) or `/rest/api` (Server/DC) |
| `CONFLUENCE_AUTH_TYPE` | `basic` or `bearer` | `basic` |
| `CONFLUENCE_EMAIL` | Email address (basic auth only) | `user@company.com` |
| `CONFLUENCE_API_TOKEN` | API token or personal access token | `ATATT3x...` |
| `CONFLUENCE_PROFILE` | Named profile to use (optional) | `staging` |
| `CONFLUENCE_READ_ONLY` | Block all write operations when `true` | `true` |
| `CONFLUENCE_FORCE_CLOUD` | Force Cloud link format for custom domains | `true` |

**Cloud vs Server/DC:**
- Atlassian Cloud (`*.atlassian.net`): use `CONFLUENCE_API_PATH`, auth type `basic` with email + API token
- Atlassian Cloud (scoped token): use `CONFLUENCE_DOMAIN="api.atlassian.com"`, `CONFLUENCE_API_PATH="/ex/confluence/<your-cloud-id>/wiki/rest/api"`, auth type `basic` with email + scoped token. Get your Cloud ID from `https://<your-site>.atlassian.net/_edge/tenant_info`. Recommended for agents (least privilege).

**Scoped API token for agents (recommended):**

`.env` example (ignored file):

```sh
CONFLUENCE_DOMAIN="api.atlassian.com"
CONFLUENCE_API_PATH="/ex/confluence/<your-cloud-id>/wiki/rest/api"
CONFLUENCE_AUTH_TYPE="basic"
CONFLUENCE_EMAIL="user@company.com"
CONFLUENCE_API_TOKEN="your-scoped-token"
```

Required classic scopes for scoped tokens:
- Read-only: `read:confluence-content.all`, `read:confluence-content.summary`, `read:confluence-space.summary`
- Write: add `write:confluence-content`

## Set up validation

To verify if the tool is properly set up, simply just check that both environment variables are non-empty: `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN`.

---

## Page ID Resolution

Most commands accept `<pageId>` — a numeric ID or any of the supported URL formats below.

**Supported formats:**

| Format | Example |
|---|---|
| Numeric ID | `123456789` |
| `?pageId=` URL | `https://company.atlassian.net/wiki/viewpage.action?pageId=123456789` |
| Pretty `/pages/<id>` URL | `https://company.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title` |
| Display `/display/<space>/<title>` URL | `https://company.atlassian.net/wiki/display/SPACE/Page+Title` |

```sh
confluence read 123456789
confluence read "https://company.atlassian.net/wiki/viewpage.action?pageId=123456789"
confluence read "https://company.atlassian.net/wiki/spaces/MYSPACE/pages/123456789/My+Page"
```

> **Note:** Display-style URLs (`/display/<space>/<title>`) perform a title-based lookup, so the page title in the URL must match exactly. When possible, prefer numeric IDs or `/pages/<id>` URLs for reliability.

## Content Formats

| Format | Notes |
|---|---|
| `markdown` | Recommended for agent-generated content. Automatically converted by the API. |
| `storage` | Confluence XML storage format (default for create/update). Use for programmatic round-trips. |
| `html` | Raw HTML. |
| `text` | Plain text — for read/export output only, not for creation. |

---

## Commands Reference

### `init`

Initialize configuration. Saves credentials to `~/.confluence-cli/config.json`.

```sh
confluence init [--read-only]
```

All flags are optional.

---

### `read <pageId>`

Read page content. Outputs to stdout.

```sh
confluence read <pageId> [--format html|text|markdown]
```

| Option | Default | Description |
|---|---|---|
| `--format` | `text` | Output format: `html`, `text`, or `markdown` |

```sh
confluence read 123456789
confluence read 123456789 --format markdown
```

---

### `info <pageId>`

Get page metadata (title, ID, type, status, space).

```sh
confluence info <pageId>
```

```sh
confluence info 123456789
```

---

### `spaces`

List all accessible Confluence spaces (key and name).

```sh
confluence spaces
```

---

### `children <pageId>`

List child pages of a page.

```sh
confluence children <pageId> [--recursive] [--max-depth <number>] [--format list|tree|json] [--show-id] [--show-url]
```

| Option | Default | Description |
|---|---|---|
| `--recursive` | false | List all descendants recursively |
| `--max-depth` | `10` | Maximum depth for recursive listing |
| `--format` | `list` | Output format: `list`, `tree`, or `json` |
| `--show-id` | false | Show page IDs |
| `--show-url` | false | Show page URLs |

```sh
confluence children 123456789
confluence children 123456789 --recursive --format json
confluence children 123456789 --recursive --format tree --show-id
```

---

### `create-child <title> <parentId>`

Create a child page under an existing page. Inherits the parent's space automatically.

```sh
confluence create-child <title> <parentId> [--content <string>] [--file <path>] [--format storage|html|markdown]
```

Options are identical to `create`. Either `--content` or `--file` is required.

```sh
confluence create-child "Chapter 1" 123456789 --content "Content here" --format markdown
confluence create-child "API Guide" 123456789 --file ./api.md --format markdown
```

---

### `update <pageId>`

Update an existing page's title and/or content. At least one of `--title`, `--content`, or `--file` is required.

```sh
confluence update <pageId> [--title <title>] [--content <string>] [--file <path>] [--format storage|html|markdown]
```

| Option | Default | Description |
|---|---|---|
| `--title` | — | New title |
| `--content` | — | Inline content string |
| `--file` | — | Path to content file |
| `--format` | `storage` | Content format |

```sh
confluence update 123456789 --title "New Title"
confluence update 123456789 --file ./updated.md --format markdown
confluence update 123456789 --title "New Title" --file ./updated.xml --format storage
```

---

### `edit <pageId>`

Fetch a page's raw storage-format content for editing locally.

```sh
confluence edit <pageId> [--output <file>]
```

| Option | Description |
|---|---|
| `--output` | Save content to a file (instead of printing to stdout) |

```sh
confluence edit 123456789 --output ./page.xml
# Edit page.xml, then:
confluence update 123456789 --file ./page.xml --format storage
```

---

### `export <pageId>`

Export a page and its attachments to a local directory.

```sh
confluence export <pageId> [--format html|text|markdown] [--dest <directory>] [--file <filename>] [--attachments-dir <name>] [--pattern <glob>] [--referenced-only] [--skip-attachments]
```

| Option | Default | Description |
|---|---|---|
| `--format` | `markdown` | Content format for the exported file |
| `--dest` | `.` | Base directory to export into |
| `--file` | `page.<ext>` | Filename for the content file |
| `--attachments-dir` | `attachments` | Subdirectory name for attachments |
| `--pattern` | — | Glob filter for attachments (e.g. `*.png`) |
| `--referenced-only` | false | Only download attachments referenced in the page content |
| `--skip-attachments` | false | Do not download attachments |

```sh
confluence export 123456789 --format markdown --dest ./docs
confluence export 123456789 --format markdown --dest ./docs --skip-attachments
confluence export 123456789 --pattern "*.png" --dest ./output
```

Creates a subdirectory named after the page title under `--dest`.

---

### `profile list`

List all configuration profiles with the active profile marked.

```sh
confluence profile list
```

---

### `profile use <name>`

Switch the active configuration profile.

```sh
confluence profile use <name>
```

```sh
confluence profile use staging
```

---

### `profile add <name>`

Add a new configuration profile. Supports the same options as `init` (interactive, non-interactive, or hybrid).

```sh
confluence profile add <name> [--domain <domain>] [--api-path <path>] [--auth-type basic|bearer] [--email <email>] [--token <token>] [--protocol http|https] [--read-only]
```

Profile names may contain letters, numbers, hyphens, and underscores only.

```sh
confluence profile add staging --domain "staging.example.com" --auth-type bearer --token "xyz"
```

---

### `profile remove <name>`

Remove a configuration profile (prompts for confirmation). Cannot remove the only remaining profile.

```sh
confluence profile remove <name>
```

```sh
confluence profile remove staging
```

---

### `stats`

Show local usage statistics.

```sh
confluence stats
```

---

### `convert`

Convert between content formats locally without a Confluence server connection.

```sh
confluence convert [--input-file <path>] [--output-file <path>] --input-format <format> --output-format <format>
```

| Option | Default | Description |
|---|---|---|
| `--input-file`, `-i` | stdin | Input file path |
| `--output-file`, `-o` | stdout | Output file path |
| `--input-format` | — | Input format: `markdown`, `storage`, `html` (required) |
| `--output-format` | — | Output format: `markdown`, `storage`, `html`, `text` (required) |

Supported conversions: markdown→storage, markdown→html, markdown→text, html→storage, html→text, html→markdown, storage→markdown, storage→html, storage→text.

```sh
# Markdown to Confluence storage format
confluence convert -i doc.md -o doc.xml --input-format markdown --output-format storage

# Pipe via stdin/stdout
echo "# Hello" | confluence convert --input-format markdown --output-format storage

# Storage format back to markdown
confluence convert -i page.xml --input-format storage --output-format markdown
```

---

## Common Agent Workflows

### Read → Edit → Update (round-trip)

```sh
# 1. Fetch raw storage XML
confluence edit 123456789 --output ./page.xml

# 2. Modify page.xml with your tool of choice

# 3. Push the updated content
confluence update 123456789 --file ./page.xml --format storage
```

### Build a documentation hierarchy

```sh
# Have a root page the ID (e.g. 111222333)
# Add children under it
confluence create-child "Architecture" 111222333 --content "# Architecture" --format markdown
confluence create-child "API Reference" 111222333 --file ./api.md --format markdown
confluence create-child "Runbooks" 111222333 --content "# Runbooks" --format markdown
```

### Offline format conversion

```sh
# Convert markdown to Confluence storage format (no server needed)
confluence convert -i doc.md -o doc.xml --input-format markdown --output-format storage

# Convert storage format to markdown for editing
confluence convert -i page.xml -o page.md --input-format storage --output-format markdown
```

### Export a page for local editing

```sh
confluence export 123456789 --format markdown --dest ./local-docs
# => ./local-docs/<page-title>/page.md + ./local-docs/<page-title>/attachments/
```

### Process children as JSON

```sh
confluence children 123456789 --recursive --format json | jq '.[].id'
```

---

## Agent Tips

- **Prefer `--format markdown`** when creating or updating content from agent-generated text — it's the most natural format and the API converts it automatically.
- **Use `--format json`** on `children` and `comments` for machine-parseable output.
- **ANSI color codes**: stdout may contain ANSI escape sequences. Pipe through `| cat` or use `NO_COLOR=1` if your downstream tool doesn't handle them.
- **Page ID vs URL**: when you have a Confluence URL, extract `?pageId=<number>` and pass the number. Do not pass pretty/display URLs — they are not supported.
- **Multiple instances**: Use `--profile <name>` or `CONFLUENCE_PROFILE` env var to target different Confluence instances without reconfiguring.

## Error Patterns

| Error | Cause | Fix |
|---|---|---|
| `No configuration found` | No config file and no env vars set | Set env vars or run `confluence init` |
| 400 on inline comment creation | Editor metadata required | Use `--location footer` or reply to existing inline comment with `--parent` |
| `File not found: <path>` | `--file` path doesn't exist | Check the path before calling the command |
| `At least one of --title, --file, or --content must be provided` | `update` called with no content options | Provide at least one of the required options |
| `Profile "<name>" not found!` | Specified profile doesn't exist | Run `confluence profile list` to see available profiles |
| `Cannot delete the only remaining profile.` | Tried to remove the last profile | Add another profile before removing |
| `This profile is in read-only mode` | Write command used with a read-only profile | Use a writable profile or remove `readOnly` from config |
