# calculator-cli

`calculator-cli` is a small command-line calculator with `mpmath` at its core and live ECB currency conversion built in.

It is designed for fast interactive use:
- `calc` and `c` launch the REPL
- `mpmath` gives you arbitrary precision math
- `convert(...)` pulls ECB FX rates and prints the rate date
- Python 3.13+ gets the modern interactive shell instead of `code.interact()`

## Install

```bash
uv sync
```

## Run

```bash
uv run calc

uv run c
```

Help:

```bash
uv run calc --help
```

## REPL

Once the shell opens, you can use ordinary `mpmath` names directly:

```python
sqrt(2)
pi + 2
quad(lambda x: exp(-x**2), [0, inf])
```

Currency conversion uses the ECB daily reference rates:

```python
convert(100, "USD", "EUR")
convert(250, "GBP", "JPY")
```

The printed conversion result is minimal: it shows only `on YYYY-MM-DD`, rendered in italics when your terminal supports ANSI styling.

## Notes

- The package requires Python `3.13` or newer.
- FX data is fetched directly from the ECB XML feed and cached locally if the network is unavailable.
- The cache is stored under your per-user cache directory:
  - Windows: `%LOCALAPPDATA%\calculator-cli\ecb_rates.xml`
  - Unix-like systems: `${XDG_CACHE_HOME:-~/.cache}/calculator-cli/ecb_rates.xml`
- The REPL namespace stays minimal: `mpmath` names plus `convert`.

## License

This package is distributed under [Apache-2.0 License](LICENSE). **This means that you can use the code freely for academic, personal, or commercial purposes!** _If you use my code extensively, I would greatly appreciate if you could credit me by linking my GitHub profile [`@alex180500`](https://github.com/alex180500) or just reference me in any way._
