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

## Test output

See [Document-AI-tion](https://paylocity.atlassian.net/wiki/spaces/MOB/pages/3112108456/Document-AI-tion) Confluence page for sample output.