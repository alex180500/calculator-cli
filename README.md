# calculator-cli

`calculator-cli` opens an embedded Python console with `mpmath` loaded into the namespace and ECB exchange conversion built in. The package is available on PyPI at [calculator-cli](https://pypi.org/project/calculator-cli/).

## Downloads

Latest release is on [GitHub Releases](https://github.com/alex180500/calculator-cli/releases/latest). Standalone binaries are available for Windows, macOS, and Linux:

- [Windows x86_64 binary](https://github.com/alex180500/calculator-cli/releases/latest/download/calculator-windows-x86_64.zip)
- [macOS arm64 binary](https://github.com/alex180500/calculator-cli/releases/latest/download/calculator-macos-arm64.tar.gz)
- [macOS x86_64 binary](https://github.com/alex180500/calculator-cli/releases/latest/download/calculator-macos-x86_64.tar.gz)
- [Linux x86_64 binary](https://github.com/alex180500/calculator-cli/releases/latest/download/calculator-linux-x86_64.tar.gz)

Each archive contains both commands:

- `calculator`
- `c`

After downloading, you can extract the archive and either run the binaries directly or move them to a directory in your `PATH`.

> [!IMPORTANT]
> Standalone binaries are built with PyInstaller and published to the latest GitHub release. On macOS and Linux, extract the archive and run `chmod +x calculator c` before the first launch if needed.

Examples:

```powershell
calculator.exe --help
c.exe
```

```bash
chmod +x calculator c
./calculator --help
./c
```

---

It's also possible to install the package with `pip`

```bash
pip install calculator-cli
```

## Run

You can run the REPL with

```bash
calculator
```

Help message

```bash
calculator --help
```

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

## Exchange cache

On every startup the app runs `refresh_exchange()`.

- The cache file is `ecb_rates.json`.
- The file stores the ECB rate date, the local retrieval date, and the currency table.
- If the cache was already retrieved today, no network request is made.
- If today is different, the app fetches the ECB XML feed again and rewrites the cache.

Default cache location:

- Windows: `%LOCALAPPDATA%\calculator-cli\ecb_rates.json`
- Unix-like systems: `${XDG_CACHE_HOME:-~/.cache}/calculator-cli/ecb_rates.json`

You can also specify a custom cache location with the `--cache` option

```bash
calculator --cache ./cache
```

## Local Install

```bash
git clone https://github.com/alex180500/calculator-cli.git
cd calculator-cli
uv sync
```

Then you can run the REPL with `uv run calculator` or `uv run c`.

## License

This package is distributed under [Apache-2.0 License](LICENSE). **This means that you can use the code freely for academic, personal, or commercial purposes!** _If you use my code extensively, I would greatly appreciate if you could credit me by linking my GitHub profile [`@alex180500`](https://github.com/alex180500) or just reference me (Alessandro Romancino) in any way._
