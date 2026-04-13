# calculator-cli

Interactive calculator REPL built on `mpmath` with `mp.dps = 100` by default.

It also includes live currency conversion using the European Central Bank daily reference rates, fetched directly from the ECB XML feed at runtime.

## Install

```bash
uv sync
```

## Run

```bash
uv run calc
uv run c
```

Show help:

```bash
uv run calc --help
```

## In the REPL

```python
sqrt(2)
convert(100, "USD", "EUR")
```

`convert(...)` prints the converted amount together with the ECB rate date and when that rate data was loaded, whether from the network or the local cache.
