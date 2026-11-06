"""Compatibility entrypoint; experiment orchestration awaits a sprint registration."""
from .config import from_args
from .runner import run_agent

def main(argv=None):
    config = from_args(argv)
    if config.stub:
        raise RuntimeError("stub mode refuses to start any subprocess")
    raise RuntimeError("Foundation only: no experiment entrypoint is enabled")

if __name__ == "__main__":
    main()
