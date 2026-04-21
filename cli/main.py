"""CLI — launches the documentation.agent.md via Copilot SDK."""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path

import yaml
from copilot import CopilotClient
from copilot.client import SubprocessConfig
from copilot.session import PermissionHandler, SessionEventType

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
AGENT_FILE = WORKSPACE_ROOT / ".github" / "agents" / "documentation.agent.md"
ENV_FILE = WORKSPACE_ROOT / ".env"


def _load_env(path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ."""
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        if key:
            os.environ.setdefault(key.strip(), value.strip())


def _parse_agent_file(path: Path) -> tuple[str, str]:
    """Return (model, system_prompt) parsed from the agent markdown file."""
    text = path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"No YAML front matter found in {path}")
    fm = yaml.safe_load(match.group(1)) or {}
    model = fm.get("model")
    if not model:
        raise ValueError(f"No model specified in {path}")
    return model, match.group(2).strip()


async def run(module: str, project_path: Path) -> None:
    model, system_prompt = _parse_agent_file(AGENT_FILE)
    _load_env(ENV_FILE)

    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN not set (check .env or environment)", file=sys.stderr)
        sys.exit(1)

    config = SubprocessConfig(
        github_token=github_token,
        use_logged_in_user=False,
    )

    async with CopilotClient(config) as client:
        async with await client.create_session(
            agent="documentation",
            on_permission_request=PermissionHandler.approve_all,
            system_message={"content": system_prompt},
        ) as session:
            done = asyncio.Event()

            def on_event(event):
                if event.type == SessionEventType.ASSISTANT_MESSAGE:
                    if event.data.content:
                        print(event.data.content)
                elif event.type == SessionEventType.SESSION_IDLE:
                    done.set()

            session.on(on_event)
            await session.send(
                f"Generate documentation for the '{module}' module.\n"
                f"Project path: {project_path}"
            )
            await done.wait()


def main():
    parser = argparse.ArgumentParser(
        description="Launch the documentation agent for a module.",
    )
    parser.add_argument("module", help="Module/package name to document (e.g. Punch).")
    parser.add_argument("project", help="Path to the source project to analyze.")
    args = parser.parse_args()

    project_path = Path(args.project).resolve()
    if not project_path.is_dir():
        print(f"Error: Project path not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    if not AGENT_FILE.is_file():
        print(f"Error: Agent file not found: {AGENT_FILE}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run(args.module, project_path))


if __name__ == "__main__":
    main()
