"""Run cli/main.py for each module in the list.

Update the `MODULES` list below before running this script.
The script runs the selected modules concurrently against the project path
defined in `PROJECT_PATH`.
"""

import asyncio
import sys
from pathlib import Path

from main import AGENT_FILE, run

MODULES = [
    # "calendar",
    # "recognition-and-rewards",
    # "cost-centers",
    # "onboarding",
    # "retirement",
    # "scheduling",
]

PROJECT_PATH = Path("#android/ios project path here")


async def run_one(module: str):
    print(f"\n{'='*60}")
    print(f"  Running: {module}")
    print(f"{'='*60}\n")
    await run(module, PROJECT_PATH)


async def run_all():
    await asyncio.gather(*(run_one(m) for m in MODULES))


def main():
    if not PROJECT_PATH.is_dir():
        print(f"Error: Project path not found: {PROJECT_PATH}", file=sys.stderr)
        sys.exit(1)
    if not AGENT_FILE.is_file():
        print(f"Error: Agent file not found: {AGENT_FILE}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_all())


if __name__ == "__main__":
    main()
