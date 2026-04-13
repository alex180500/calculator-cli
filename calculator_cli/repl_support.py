import builtins
import sys
from types import ModuleType

import mpmath as mp

from calculator_cli.fx import convert, format_conversion

mp.mp.dps = 100


def displayhook(value: object) -> None:
    if value is None:
        return

    setattr(builtins, "_", value)
    formatted_conversion = format_conversion(value)
    if formatted_conversion is not None:
        if sys.stdout.isatty():
            print(f"\x1b[3m{formatted_conversion}\x1b[0m")
        else:
            print(formatted_conversion)
        return

    try:
        print(mp.nstr(mp.chop(value), 16))
    except Exception:
        print(repr(value))


def install_displayhook() -> None:
    sys.displayhook = displayhook


def _is_public_mpmath_name(name: str, value: object) -> bool:
    if name.startswith("_"):
        return False
    if name in {"mp", "fp", "iv"}:
        return False
    if isinstance(value, type) or isinstance(value, ModuleType):
        return False
    return True


def build_namespace() -> dict[str, object]:
    namespace = {
        name: value
        for name in dir(mp)
        if (value := getattr(mp, name)) is not None
        and _is_public_mpmath_name(name, value)
    }
    namespace["convert"] = convert
    return namespace
