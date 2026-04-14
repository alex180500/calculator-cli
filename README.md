# calculator-cli

`calculator-cli` opens an embedded Python console with `mpmath` loaded into the namespace and ECB exchange conversion built in.

## REPL Usage

Normal Python expressions stay normal Python expressions:

```python
1 / 3
2 ** 10
```

The `_` variable is stored as the last result and can be used as in the usual Python REPL.

`mpmath` names are already loaded, so `mpmath` expressions work directly:

```python
sin(pi)
sqrt(2)
quad(lambda x: exp(-x**2), [0, inf])
```

`sin(pi)` is displayed as `0` because the REPL display hook uses `mpmath.chop(...)` before printing.

Exchange helpers are also available:

```python
convert(100, "EUR", "USD")
refresh_exchange()
```

`convert(...)` returns an `mpmath.mpf`, so `_` stays numeric and can be reused in later calculations. In the REPL it is displayed as:

```text
116.84 USD [on 2026-04-13]
```

## Run

```bash
uv run calculator
uv run c
```

Help:

```bash
uv run calculator --help
```

Custom cache directory:

```bash
uv run calculator --cache ./cache
```


## Exchange cache

On every startup the app runs `refresh_exchange()`.

- The cache file is `ecb_rates.json`.
- The file stores the ECB rate date, the local retrieval date, and the currency table.
- If the cache was already retrieved today, no network request is made.
- If today is different, the app fetches the ECB XML feed again and rewrites the cache.

Default cache location:

- Windows: `%LOCALAPPDATA%\calculator-cli\ecb_rates.json`
- Unix-like systems: `${XDG_CACHE_HOME:-~/.cache}/calculator-cli/ecb_rates.json`


## Local Install

```bash
uv sync

uv run calculator
```

## License

This package is distributed under the [Apache-2.0 License](LICENSE).
