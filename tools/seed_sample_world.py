from __future__ import annotations

from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    print(f'sample world is already bundled at: {project_root / "data" / "worlds" / "sample_world"}')


if __name__ == '__main__':
    main()
