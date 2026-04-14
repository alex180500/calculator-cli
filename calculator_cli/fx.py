import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from mpmath import mpf

ECB_DAILY_XML_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
CACHE_DIR_ENV = "CALCULATOR_CLI_CACHE_DIR"
CACHE_FILE_NAME = "ecb_rates.json"


class CurrencyRateError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RateSnapshot:
    rate_date: str
    retrieved_on: str
    rates: dict[str, mpf]


def default_cache_dir() -> Path:
    if os.name == "nt":
        cache_path = os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
    else:
        cache_path = os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")
    return Path(cache_path) / "calculator-cli"


def resolve_cache_dir(cache_dir: str | os.PathLike[str] | None = None) -> Path:
    if cache_dir is None:
        return default_cache_dir()
    return Path(cache_dir).expanduser().resolve()


class FXRates:
    def __init__(
        self,
        xml_url: str = ECB_DAILY_XML_URL,
        cache_dir: str | os.PathLike[str] | None = None,
    ) -> None:
        self.xml_url = xml_url
        self.cache_dir = resolve_cache_dir(cache_dir)
        self.cache_path = self.cache_dir / CACHE_FILE_NAME
        self.snapshot: RateSnapshot | None = None
        self._cache_loaded = False
        self._last_failed_refresh_on: str | None = None
        self._last_refresh_error: CurrencyRateError | None = None

    def _today(self) -> str:
        return date.today().isoformat()

    def _load_cache(self) -> None:
        if self._cache_loaded:
            return

        self._cache_loaded = True
        if not self.cache_path.exists():
            return

        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        if not isinstance(payload, dict):
            return

        rate_date = payload.get("rate_date")
        retrieved_on = payload.get("retrieved_on")
        rates = payload.get("rates")
        if (
            not isinstance(rate_date, str)
            or not isinstance(retrieved_on, str)
            or not isinstance(rates, dict)
        ):
            return

        try:
            parsed_rates = {
                currency: mpf(rate)
                for currency, rate in rates.items()
                if isinstance(currency, str) and isinstance(rate, str)
            }
        except (TypeError, ValueError):
            return

        if len(parsed_rates) != len(rates) or "EUR" not in parsed_rates:
            return

        self.snapshot = RateSnapshot(
            rate_date=rate_date,
            retrieved_on=retrieved_on,
            rates=parsed_rates,
        )

    def _write_cache(self) -> None:
        if self.snapshot is None:
            return

        payload = {
            "rate_date": self.snapshot.rate_date,
            "retrieved_on": self.snapshot.retrieved_on,
            "rates": {
                currency: str(rate) for currency, rate in self.snapshot.rates.items()
            },
        }
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(payload, separators=(",", ":")),
            encoding="utf-8",
        )

    def _parse_rates(self, payload: bytes) -> tuple[str, dict[str, mpf]]:
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            raise CurrencyRateError("ECB response was not valid XML.") from exc

        cube_time = next(
            (
                node
                for node in root.iter()
                if node.tag.rsplit("}", 1)[-1] == "Cube" and "time" in node.attrib
            ),
            None,
        )
        if cube_time is None:
            raise CurrencyRateError("ECB response did not include a rates date.")

        rates: dict[str, mpf] = {"EUR": mpf("1")}
        for cube in cube_time:
            if cube.tag.rsplit("}", 1)[-1] != "Cube":
                continue

            currency = cube.attrib.get("currency")
            rate = cube.attrib.get("rate")
            if not currency or not rate:
                continue

            try:
                rates[currency.upper()] = mpf(rate)
            except (TypeError, ValueError) as exc:
                raise CurrencyRateError(
                    f"ECB response included an invalid rate for {currency!r}."
                ) from exc

        if len(rates) == 1:
            raise CurrencyRateError("ECB response did not include any exchange rates.")

        return cube_time.attrib["time"], rates

    def _fetch_rates(self) -> tuple[str, dict[str, mpf]]:
        try:
            with urllib.request.urlopen(self.xml_url, timeout=10) as response:
                payload = response.read()
        except urllib.error.URLError as exc:
            raise CurrencyRateError(
                f"Unable to fetch ECB exchange rates: {exc}"
            ) from exc

        return self._parse_rates(payload)

    def refresh_exchange(self, force: bool = False) -> str:
        self._load_cache()
        today = self._today()

        if (
            not force
            and self.snapshot is not None
            and self.snapshot.retrieved_on == today
        ):
            return self.snapshot.rate_date

        if not force and self._last_failed_refresh_on == today:
            if self.snapshot is not None:
                return self.snapshot.rate_date
            if self._last_refresh_error is not None:
                raise self._last_refresh_error
            raise CurrencyRateError("Exchange rates are not available.")

        try:
            rate_date, rates = self._fetch_rates()
        except CurrencyRateError as exc:
            self._last_failed_refresh_on = today
            self._last_refresh_error = exc
            if self.snapshot is not None:
                return self.snapshot.rate_date
            raise

        self.snapshot = RateSnapshot(
            rate_date=rate_date,
            retrieved_on=today,
            rates=rates,
        )
        self._last_failed_refresh_on = None
        self._last_refresh_error = None

        try:
            self._write_cache()
        except OSError:
            pass

        return rate_date

    def convert(
        self,
        amount: object,
        from_currency: str,
        to_currency: str,
        refresh: bool = False,
    ) -> mpf:
        if refresh:
            self.refresh_exchange(force=True)
        else:
            self.refresh_exchange(force=False)

        if self.snapshot is None:
            if self._last_refresh_error is not None:
                raise self._last_refresh_error
            raise CurrencyRateError("Exchange rates are not available.")

        source = from_currency.upper()
        target = to_currency.upper()
        if source not in self.snapshot.rates:
            raise CurrencyRateError(f"Unsupported source currency: {source}")
        if target not in self.snapshot.rates:
            raise CurrencyRateError(f"Unsupported target currency: {target}")

        amount_value = mpf(amount)
        amount_in_eur = (
            amount_value
            if source == "EUR"
            else amount_value / self.snapshot.rates[source]
        )
        converted = (
            amount_in_eur
            if target == "EUR"
            else amount_in_eur * self.snapshot.rates[target]
        )
        return converted


_default_rates: FXRates | None = None


def configure_default_rates(
    cache_dir: str | os.PathLike[str] | None = None,
) -> FXRates:
    global _default_rates
    _default_rates = FXRates(cache_dir=cache_dir)
    return _default_rates


def get_default_rates() -> FXRates:
    global _default_rates
    if _default_rates is None:
        _default_rates = FXRates(cache_dir=os.environ.get(CACHE_DIR_ENV))
    return _default_rates


def refresh_exchange(force: bool = False) -> str:
    return get_default_rates().refresh_exchange(force=force)


def convert(
    amount: object,
    from_currency: str,
    to_currency: str,
    refresh: bool = False,
) -> mpf:
    return get_default_rates().convert(
        amount,
        from_currency,
        to_currency,
        refresh=refresh,
    )
