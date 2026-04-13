from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from calculator_cli.repl_support import build_namespace, install_displayhook


def bootstrap(namespace: MutableMapping[str, Any] | None = None) -> None:
    namespace = globals() if namespace is None else namespace
    namespace.update(build_namespace())
    install_displayhook()


if __name__ == "__main__":
    bootstrap()
