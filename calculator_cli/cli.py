from __future__ import annotations

import subprocess
import sys

HELP_BANNER = (
    "calculator-cli\n"

    "Loaded: mpmath.*, convert(amount, from_currency, to_currency)\n"

    "Uses the Python 3.13+ interactive shell when available\n"
    "convert(...) pretty prints the result with the ECB rate date\n"
    "ECB FX cache lives in your per-user cache directory\n"
    "Precision: mp.dps = 100\n"
    
    "Examples:\n"
    "  sqrt(2)\n"
    "  quad(lambda x: exp(-x**2), [0, inf])\n"
    "  convert(100, 'USD', 'EUR')"
)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if any(arg in {"-h", "--help"} for arg in args):
        print(HELP_BANNER)
        return 0

    subprocess.run(
        [
            sys.executable,
            "-q",
            "-i",
            "-c",
            "from calculator_cli.repl_bootstrap import bootstrap; bootstrap(globals())",
        ],
        check=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
