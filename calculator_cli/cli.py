import argparse
import os
from pathlib import Path
import subprocess
import sys

from calculator_cli.fx import CACHE_DIR_ENV

BOOTSTRAP_CODE = "from calculator_cli.repl import bootstrap; bootstrap(globals())"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=Path(sys.argv[0]).name or "calculator",
        description=(
            "Open the standard Python REPL with public mpmath names plus "
            "convert(...) and refresh_exchange()."
        ),
    )
    parser.add_argument(
        "--cache",
        metavar="DIR",
        help="store the ECB cache in DIR/ecb_rates.json",
    )
    return parser


def repl_command(python_executable: str | None = None) -> list[str]:
    executable = sys.executable if python_executable is None else python_executable
    return [executable, "-q", "-i", "-c", BOOTSTRAP_CODE]


def build_repl_env(cache_dir: str | None = None) -> dict[str, str]:
    env = os.environ.copy()
    if cache_dir:
        env[CACHE_DIR_ENV] = str(Path(cache_dir).expanduser().resolve())
    return env


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    completed = subprocess.run(
        repl_command(),
        check=False,
        env=build_repl_env(args.cache),
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
