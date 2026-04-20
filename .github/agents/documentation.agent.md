---
description: Generate documentation for the project. (master agent)
tools: [agent, search]
model: GPT-4.1
argument-hint: Generate a documentation for Punch module
---

Orchestrate the documentation generation process from the source code by running dedicated agents.

# Requirements
- User MUST provide a specific package/module identification (for example by name). Ask for clarification if the input is ambiguous.

# API documentation
Run `api-communication.agent` to generate comprehensive API documentation for the specified package/module.

# Output
Print all documentation to standard output in markdown format.