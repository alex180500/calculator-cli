import argparse

from calculator_cli.repl import start_console

HELP_TEXT = """\x1b[1;34mExtra functions:\x1b[0m\n
  \x1b[36mconvert\x1b[0m(\x1b[33mamount\x1b[0m, \x1b[33mfrom_currency\x1b[0m, \x1b[33mto_currency\x1b[0m)\n
  \x1b[36mrefresh_exchange\x1b[0m()\n\n

\x1b[1;34mExamples:\x1b[0m\n
  1 / 3\n
  e**2 + 1\n
  sin(pi)\n
  convert(100, "EUR", "USD")\n
  refresh_exchange()\n
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="calculator",
        description="A calculator REPL CLI with mpmath and ECB exchange rates",
        epilog=HELP_TEXT,
    )
    parser.add_argument(
        "--cache",
        metavar="DIR",
        help="store the ECB cache in DIR/ecb_rates.json",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start_console(cache_dir=args.cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
