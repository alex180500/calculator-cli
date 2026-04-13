from calculator_cli.repl_support import build_namespace, install_displayhook


def bootstrap(namespace: dict[str, object] | None = None) -> None:
    namespace = globals() if namespace is None else namespace
    namespace.update(build_namespace())
    install_displayhook()


if __name__ == "__main__":
    bootstrap()
