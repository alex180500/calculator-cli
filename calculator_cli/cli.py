from __future__ import annotations

import builtins
import code
import inspect
import sys
from typing import Any

import mpmath as mp

from calculator_cli.fx import convert, format_conversion

HELP_BANNER = (
    "calculator-cli\n"
    "Loaded: mpmath.*, convert(amount, from_currency, to_currency)\n"
    "convert(...) prints the ECB rate date and rate-load time\n"
    "Precision: mp.dps = 100\n"
    "FX source: ECB latest euro foreign exchange reference rates\n"
    "Examples:\n"
    "  sqrt(2)\n"
    "  quad(lambda x: exp(-x**2), [0, inf])\n"
    "  convert(100, 'USD', 'EUR')"
)
mp.mp.dps = 100


def dh(x: Any) -> None:
    if x is not None:
        setattr(builtins, "_", x)
        formatted_conversion = format_conversion(x)
        if formatted_conversion is not None:
            print(formatted_conversion)
            return
        try:
            print(mp.nstr(mp.chop(x), 16))
        except Exception:
            print(repr(x))


def _is_public_mpmath_name(name: str, value: Any) -> bool:
    if name.startswith("_"):
        return False
    if name in {"mp", "fp", "iv"}:
        return False
    if inspect.isclass(value) or inspect.ismodule(value):
        return False
    if value.__class__.__name__.endswith("Context"):
        return False
    return True


def build_namespace() -> dict[str, Any]:
    ns = {
        name: value
        for name in dir(mp)
        if (value := getattr(mp, name)) is not None
        and _is_public_mpmath_name(name, value)
    }
    ns["convert"] = convert
    return ns


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if any(arg in {"-h", "--help"} for arg in args):
        print(HELP_BANNER)
        return 0

    sys.displayhook = dh
    code.interact(banner="", local=build_namespace())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
