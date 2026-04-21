# experimental-document-ai-tion

AI-powered documentation generator for mobile apps. Uses GitHub Copilot agents and skills to analyze Android/iOS source code and publish structured documentation to Confluence.

## Setup

1. **Install dependencies**

   ```sh
   npm install
   ```

2. **Configure environment**

   Copy `.env.example` to `.env` (ignored file) and fill in your credentials:

   ```sh
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `CONFLUENCE_EMAIL` | Your Atlassian account email |
   | `CONFLUENCE_API_TOKEN` | API token from [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |

3. **Add source repositories**

   Clone `mobile-next-gen-ios` and `mobile-next-gen-android` into the project root. These directories are gitignored.

4. **Set up `GITHUB_TOKEN`**

   The Copilot SDK requires a GitHub personal access token. Add it to your `.env`:

   ```
   GITHUB_TOKEN=<your-github-pat>
   ```

   Generate one at [GitHub → Settings → Developer settings → Personal access tokens (fine-grained)](https://github.com/settings/tokens).

5. **Install Python dependencies**

   ```sh
   python3.11 -m pip install -r requirements.txt
   ```

## CLI Usage

```sh
python3.11 -m cli.main <module> <project>
```

| Argument | Description |
|---|---|
| `module` | Module/package name to document (e.g. `Punch`) |
| `project` | Path to the source project to analyze |

**Example:**

```sh
python3.11 -m cli.main Punch ./mobile-next-gen-ios
```

This launches the documentation agent, which analyzes the given module in the source project and publishes structured documentation to Confluence.

## Test output

See [Document-AI-tion](https://paylocity.atlassian.net/wiki/spaces/MOB/pages/3112108456/Document-AI-tion) Confluence page for sample output.