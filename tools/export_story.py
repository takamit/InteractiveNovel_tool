from __future__ import annotations

from pathlib import Path

from core.logic.application import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    app = create_app(project_root)
    app.run_turns(turns=2, autosave=False)
    output_path = project_root / 'data' / 'exports' / 'stories' / 'latest_story.txt'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(app.render(mode='omniscient'), encoding='utf-8')
    print(output_path)


if __name__ == '__main__':
    main()
