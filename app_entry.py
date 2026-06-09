"""Frozen-build entry point.

PyInstaller runs its entry script as the top-level ``__main__`` module with no
parent package, which breaks the relative imports inside ``screenit/__main__``.
Importing the package's ``main`` from here keeps those imports valid.
``python -m screenit`` still works directly via ``screenit/__main__.py``.
"""

from screenit.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
