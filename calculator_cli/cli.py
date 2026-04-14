import argparse
import code
import sys

from calculator_cli.repl import prepare_session

HELP_TEXT = """\x1b[1;34musage:\x1b[0m \x1b[1;35mcalculator\x1b[0m [\x1b[1;32m-h\x1b[0m] [\x1b[1;36m--cache\x1b[0m \x1b[1;33mDIR\x1b[0m]

Open an embedded Python console with public mpmath names and ECB exchange helpers.

\x1b[1;34moptions:\x1b[0m
  \x1b[1;32m-h\x1b[0m, \x1b[32m--help\x1b[0m     show this help message and exit
  \x1b[36m--cache\x1b[0m \x1b[33mDIR\x1b[0m    store the ECB cache in DIR/ecb_rates.json

\x1b[1;34mCLI functions:\x1b[0m
  \x1b[36mexit\x1b[0m, \x1b[36mquit\x1b[0m, \x1b[36mq\x1b[0m  \x1b[37mleave the console CLI\x1b[0m

\x1b[1;34mextra functions:\x1b[0m
  \x1b[36mconvert\x1b[0m(\x1b[33mamount\x1b[0m, \x1b[33mfrom_currency\x1b[0m, \x1b[33mto_currency\x1b[0m)
  \x1b[36mrefresh_exchange\x1b[0m()

\x1b[1;34mexamples:\x1b[0m
  1 / 3
  e**2 + 1
  sin(pi)
  convert(100, "EUR", "USD")
  refresh_exchange()
"""

CLI_PS1 = "\x1b[35m:>\x1b[0m "


class CalculatorConsole(code.InteractiveConsole):
    def raw_input(self, prompt: str = "") -> str:
        line = super().raw_input(prompt)
        if line.strip() in {"q", "quit", "exit"}:
            raise EOFError
        return line


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="calculator",
        add_help=False,
    )
    parser.add_argument("--cache")
    parser.add_argument("-h", "--help", action="store_true")
    return parser.parse_args(argv)


def start_console(cache_dir: str | None = None) -> None:
    namespace: dict[str, object] = {}
    prepare_session(namespace, cache_dir=cache_dir)
    sys.ps1 = CLI_PS1
    CalculatorConsole(locals=namespace, local_exit=True).interact(
        banner="",
        exitmsg="",
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.help:
        print(HELP_TEXT, end="")
        return 0
    start_console(cache_dir=args.cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
