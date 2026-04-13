import builtins
import os
import sys
from collections.abc import Callable
from types import ModuleType

import mpmath as mp

from calculator_cli.fx import (
    CACHE_DIR_ENV,
    CurrencyRateError,
    FXRates,
    configure_default_rates,
    format_mpmath_value,
    is_mpmath_value,
)

HELP_BANNER = """calculator-cli

Runs the standard Python REPL with public `mpmath` names loaded.

Extra functions:
  convert(amount, from_currency, to_currency)
  refresh_exchange()

Options:
  -h, --help     Show this help
  --cache DIR    Store the ECB cache in DIR/ecb_rates.json

Examples:
  1 / 3
  sin(pi)
  convert(100, "EUR", "USD")
  refresh_exchange()
"""


def _is_public_mpmath_name(name: str, value: object) -> bool:
    if name.startswith("_"):
        return False
    if name in {"fp", "iv"}:
        return False
    if isinstance(value, type) or isinstance(value, ModuleType):
        return False
    return True


def build_namespace(rates: FXRates) -> dict[str, object]:
    namespace = {
        name: value
        for name in dir(mp)
        if (value := getattr(mp, name)) is not None
        and _is_public_mpmath_name(name, value)
    }
    namespace["mp"] = mp
    namespace["mpmath"] = mp
    namespace["convert"] = rates.convert
    namespace["refresh_exchange"] = rates.refresh_exchange
    return namespace


class ReplDisplayHook:
    def __init__(
        self,
        rates: FXRates,
        default_hook: Callable[[object], None] | None = None,
    ) -> None:
        self.rates = rates
        self.default_hook: Callable[[object], None] = (
            sys.__displayhook__ if default_hook is None else default_hook
        )

    def __call__(self, value: object) -> None:
        if value is None:
            return

        try:
            text = self.rates.format_conversion(value)
            if text is None and is_mpmath_value(value):
                text = format_mpmath_value(value)
            if text is None:
                self.default_hook(value)
                return

            builtins.__dict__["_"] = None
            print(text)
            builtins.__dict__["_"] = value
        except Exception:
            self.default_hook(value)


def bootstrap(
    namespace: dict[str, object] | None = None,
    cache_dir: str | None = None,
) -> FXRates:
    active_namespace = globals() if namespace is None else namespace
    rates = configure_default_rates(cache_dir or os.environ.get(CACHE_DIR_ENV))

    sys.displayhook = ReplDisplayHook(rates)
    active_namespace.update(build_namespace(rates))

    try:
        rates.refresh_exchange(force=False)
    except CurrencyRateError as exc:
        if rates.snapshot is None:
            print(f"Warning: {exc}", file=sys.stderr)

    return rates


def main() -> None:
    bootstrap(globals())


if __name__ == "__main__":
    main()
