"""Explicit runtime configuration. Importing this module performs no I/O."""
from dataclasses import dataclass
from pathlib import Path
import argparse
import os

@dataclass(frozen=True)
class Config:
    workspace: Path
    run_dir: Path
    model: str = "gpt-6.1-sol"
    reasoning_effort: str = "low"
    timeout: float = 180
    workers: int = 4
    stub: bool = True
    cli: str = "codex"

    def __post_init__(self):
        if self.timeout <= 0 or self.workers < 1:
            raise ValueError("timeout and workers must be positive")

def from_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", default=os.environ.get("EARSHOT_WORKSPACE"), required=not os.environ.get("EARSHOT_WORKSPACE"))
    parser.add_argument("--run-dir", default=os.environ.get("EARSHOT_RUN_DIR"), required=not os.environ.get("EARSHOT_RUN_DIR"))
    parser.add_argument("--model", default=os.environ.get("EARSHOT_MODEL", "gpt-6.1-sol"))
    parser.add_argument("--reasoning-effort", default=os.environ.get("EARSHOT_REASONING_EFFORT", "low"))
    parser.add_argument("--timeout", type=float, default=float(os.environ.get("EARSHOT_TIMEOUT", "180")))
    parser.add_argument("--workers", type=int, default=int(os.environ.get("EARSHOT_WORKERS", "4")))
    parser.add_argument("--cli", default=os.environ.get("EARSHOT_CLI", "codex"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args(argv)
    return Config(Path(args.workspace), Path(args.run_dir), args.model, args.reasoning_effort, args.timeout, args.workers, not args.live, args.cli)
