import builtins
import code
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
)

MPMATH_HIDDEN_NAMES = {"fp", "iv"}


def is_mpmath_value(value: object) -> bool:
    return type(value).__module__.startswith("mpmath")


def format_mpmath_value(value: object) -> str:
    chopped = mp.chop(value)
    if isinstance(chopped, (mp.mpf, mp.mpc)) and chopped == 0:
        return "0"
    return str(chopped)


def extend_namespace(
    namespace: dict[str, object],
    rates: FXRates,
    display_hook: ReplDisplayHook,
) -> None:
    for name, value in vars(mp).items():
        if name.startswith("_") or name in MPMATH_HIDDEN_NAMES:
            continue
        if isinstance(value, (type, ModuleType)):
            continue
        namespace[name] = value

    def convert(
        amount: object,
        from_currency: str,
        to_currency: str,
        refresh: bool = False,
    ) -> object:
        result = rates.convert(
            amount,
            from_currency,
            to_currency,
            refresh=refresh,
        )
        snapshot = rates.snapshot
        if snapshot is not None:
            display_hook.record_conversion(
                result, to_currency.upper(), snapshot.rate_date
            )
        return result

    namespace.update(
        mp=mp,
        mpmath=mp,
        convert=convert,
        refresh_exchange=rates.refresh_exchange,
    )


class ReplDisplayHook:
    def __init__(
        self,
        default_hook: Callable[[object], None] | None = None,
    ) -> None:
        self.default_hook: Callable[[object], None] = (
            sys.__displayhook__ if default_hook is None else default_hook
        )
        self._last_conversion: tuple[int, str, str] | None = None

    def record_conversion(self, value: object, currency: str, rate_date: str) -> None:
        self._last_conversion = (id(value), currency, rate_date)

    def __call__(self, value: object) -> None:
        if value is None:
            return

        try:
            text = None
            if self._last_conversion is not None:
                object_id, currency, rate_date = self._last_conversion
                self._last_conversion = None
                if id(value) == object_id:
                    text = f"{format_mpmath_value(value)} {currency} [on {rate_date}]"

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


class CalculatorConsole(code.InteractiveConsole):
    def raw_input(self, prompt: str = "") -> str:
        line = super().raw_input(prompt)
        if line.strip() in {"q", "quit", "exit"}:
            raise EOFError
        return line


def prepare_session(
    namespace: dict[str, object] | None = None,
    cache_dir: str | None = None,
) -> FXRates:
    if namespace is None:
        namespace = {}

    display_hook = ReplDisplayHook()
    rates = configure_default_rates(cache_dir or os.environ.get(CACHE_DIR_ENV))
    extend_namespace(namespace, rates, display_hook)
    sys.displayhook = display_hook

    try:
        rates.refresh_exchange(force=False)
    except CurrencyRateError as exc:
        if rates.snapshot is None:
            print(f"Warning: {exc}", file=sys.stderr)

    return rates


def start_console(cache_dir: str | None = None) -> FXRates:
    namespace: dict[str, object] = {}
    rates = prepare_session(namespace, cache_dir=cache_dir)
    sys.ps1 = "\x1b[35m:>\x1b[0m "
    CalculatorConsole(locals=namespace, local_exit=True).interact(
        banner="",
        exitmsg="",
    )
    return rates
