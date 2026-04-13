from dataclasses import dataclass
import os
from pathlib import Path
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from mpmath import mpf

ECB_DAILY_XML_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


class CurrencyRateError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RateSnapshot:
    rate_date: str
    rates: dict[str, mpf]


class ECBReferenceRates:
    def __init__(self) -> None:
        self._snapshot: RateSnapshot | None = None
        self._last_conversion: tuple[int, str] | None = None

    def _cache_path(self) -> Path:
        if os.name == "nt":
            base = Path(
                os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
            )
        else:
            base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        return base / "calculator-cli" / "ecb_rates.xml"

    def _parse(self, payload: bytes) -> RateSnapshot:
        root = ET.fromstring(payload)
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

        rate_date = cube_time.attrib["time"]
        rates: dict[str, mpf] = {"EUR": mpf("1")}

        for cube in cube_time:
            if cube.tag.rsplit("}", 1)[-1] != "Cube":
                continue
            currency = cube.attrib.get("currency")
            rate = cube.attrib.get("rate")
            if not currency or not rate:
                continue
            rates[currency.upper()] = mpf(rate)

        if len(rates) == 1:
            raise CurrencyRateError("ECB response did not include any exchange rates.")

        return RateSnapshot(rate_date=rate_date, rates=rates)

    def _load_cache(self) -> RateSnapshot | None:
        cache_path = self._cache_path()
        if not cache_path.exists():
            return None

        snapshot = self._parse(cache_path.read_bytes())
        self._snapshot = snapshot
        return snapshot

    def _store_cache(self, payload: bytes) -> None:
        cache_path = self._cache_path()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(payload)

    def _fetch(self) -> RateSnapshot:
        try:
            with urllib.request.urlopen(ECB_DAILY_XML_URL, timeout=10) as response:
                payload = response.read()
            snapshot = self._parse(payload)
            self._snapshot = snapshot
            try:
                self._store_cache(payload)
            except OSError:
                pass
            return snapshot
        except (urllib.error.URLError, OSError, ET.ParseError) as exc:
            cached = self._load_cache()
            if cached is not None:
                return cached
            raise CurrencyRateError(
                f"Unable to fetch ECB exchange rates and no cached data is available: {exc}"
            ) from exc

    def latest(self, refresh: bool = False) -> RateSnapshot:
        if not refresh and self._snapshot is not None:
            return self._snapshot
        return self._fetch()

    def convert(
        self,
        amount: object,
        from_currency: str,
        to_currency: str,
        refresh: bool = False,
    ) -> mpf:
        snapshot = self.latest(refresh=refresh)
        source = from_currency.upper()
        target = to_currency.upper()

        if source not in snapshot.rates:
            raise CurrencyRateError(f"Unsupported source currency: {source}")
        if target not in snapshot.rates:
            raise CurrencyRateError(f"Unsupported target currency: {target}")

        amount_value = mpf(amount)
        amount_in_eur = (
            amount_value if source == "EUR" else amount_value / snapshot.rates[source]
        )
        converted = (
            amount_in_eur if target == "EUR" else amount_in_eur * snapshot.rates[target]
        )
        self._last_conversion = (id(converted), snapshot.rate_date)
        return converted

    def format_conversion(self, value: object) -> str | None:
        if self._last_conversion is None:
            return None
        object_id, rate_date = self._last_conversion
        if id(value) != object_id:
            return None
        return f"on {rate_date}"


ecb_rates = ECBReferenceRates()


def convert(
    amount: object, from_currency: str, to_currency: str, refresh: bool = False
) -> mpf:
    return ecb_rates.convert(amount, from_currency, to_currency, refresh=refresh)


def format_conversion(value: object) -> str | None:
    return ecb_rates.format_conversion(value)
