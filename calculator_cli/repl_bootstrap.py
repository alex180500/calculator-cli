from __future__ import annotations

from calculator_cli.repl_support import build_namespace, install_displayhook


def bootstrap() -> None:
    namespace = build_namespace()
    install_displayhook()

    preserved = {
        name: value for name, value in globals().items() if name.startswith("__")
    }
    globals().clear()
    globals().update(preserved)
    globals().update(namespace)


if __name__ == "__main__":
    bootstrap()
