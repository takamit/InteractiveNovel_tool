from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from core.logic.application import SimulationApplication, create_app


class DesktopAppFacade:
    def preview(self, project_root: str | Path) -> dict[str, object]:
        app = create_app(project_root)
        app.run_turns(turns=1, autosave=False)
        return {"analysis": app.analysis(), "render": app.render(mode="protagonist")}


class SimulationDesktopRunner:
    """Lightweight desktop runner for player-driven simulation."""

    def __init__(self) -> None:
        self.root: tk.Tk | None = None
        self.app: SimulationApplication | None = None
        self.player_entity_id: str = "char_001"
        self.project_root: Path | None = None
        self.target_map: dict[str, str | None] = {}
        self.action_map: dict[str, dict[str, object]] = {}

    def _analysis_summary(self, app: SimulationApplication) -> str:
        analysis = app.analysis()
        hottest = ", ".join(f"{item['location_id']}:{item['heat']:.1f}" for item in analysis.get('hottest_locations', [])[:3]) or "なし"
        stressed = ", ".join(f"{item['entity_id']}:{item['stress']:.1f}" for item in analysis.get('highest_stress', [])[:3]) or "なし"
        return f"Turn={analysis.get('turn')} | WorldTension={analysis.get('world_tension', 0):.1f}\nHot={hottest}\nStress={stressed}"

    def _build_target_labels(self, app: SimulationApplication) -> list[str]:
        self.target_map = {"流れに任せる": None}
        labels = ["流れに任せる"]
        for item in app.list_target_options(self.player_entity_id):
            same = "同じ場所" if item['same_location'] == 'yes' else "別の場所"
            label = f"{item['name']}｜{same}｜{item['relation_hint']}"
            self.target_map[label] = item['entity_id']
            labels.append(label)
        return labels

    def _build_action_labels(self, app: SimulationApplication, target_id: str | None) -> list[str]:
        self.action_map = {}
        labels: list[str] = []
        for option in app.list_presented_player_options(self.player_entity_id, target_id=target_id):
            label = str(option['choice_label'])
            self.action_map[label] = option
            labels.append(label)
        return labels

    def run(self, project_root: str | Path, *, player_entity_id: str = "char_001") -> None:
        self.project_root = Path(project_root)
        self.player_entity_id = player_entity_id
        self.app = create_app(self.project_root)

        self.root = tk.Tk()
        self.root.title("対話式小説")
        self.root.geometry("1180x760")

        top = ttk.Frame(self.root, padding=10)
        top.pack(fill=tk.BOTH, expand=True)

        control = ttk.Frame(top)
        control.pack(fill=tk.X)

        ttk.Label(control, text="相手").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        target_var = tk.StringVar(value="流れに任せる")
        target_combo = ttk.Combobox(control, state="readonly", width=52, textvariable=target_var)
        target_combo.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(control, text="行動").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=(8, 0))
        action_var = tk.StringVar()
        action_combo = ttk.Combobox(control, state="readonly", width=82, textvariable=action_var)
        action_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W, pady=(8, 0))

        ttk.Label(control, text="表示視点").grid(row=0, column=2, sticky=tk.W, padx=(16, 8))
        mode_var = tk.StringVar(value="protagonist")
        mode_combo = ttk.Combobox(control, state="readonly", width=18, textvariable=mode_var, values=["protagonist", "omniscient", "observer", "analyst", "character"])
        mode_combo.grid(row=0, column=3, sticky=tk.W)

        detail_var = tk.StringVar(value="")
        ttk.Label(control, textvariable=detail_var).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(8, 0))

        button_frame = ttk.Frame(control)
        button_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(12, 0))

        render_box = tk.Text(top, wrap="word", height=26)
        render_box.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        analysis_box = tk.Text(top, wrap="word", height=8)
        analysis_box.pack(fill=tk.X, expand=False, pady=(12, 0))

        def refresh_actions(*_: object) -> None:
            assert self.app is not None
            target_id = self.target_map.get(target_var.get())
            presented = self.app.list_presented_player_options(self.player_entity_id, target_id=target_id)
            labels = []
            self.action_map = {}
            for item in presented:
                label = str(item['choice_label'])
                labels.append(label)
                self.action_map[label] = item
            action_combo["values"] = labels
            if labels:
                action_var.set(labels[0])
                detail_var.set(str(self.action_map[labels[0]].get('choice_detail', '')))

        def refresh_view(message: str | None = None) -> None:
            assert self.app is not None
            mode = mode_var.get()
            focal_entity_id = self.player_entity_id if mode in {"protagonist", "character", "analyst"} else None
            body = self.app.render(mode=mode, focal_entity_id=focal_entity_id) if self.app.engine.last_turn_result else "まだターンが実行されていません。"
            if message:
                body = f"{message}\n\n{body}"
            render_box.delete("1.0", tk.END)
            render_box.insert("1.0", body)
            analysis_box.delete("1.0", tk.END)
            analysis_box.insert("1.0", self._analysis_summary(self.app))

        def run_player_turn() -> None:
            assert self.app is not None
            selected_label = action_var.get()
            option = self.action_map.get(selected_label)
            if not option:
                messagebox.showwarning("対話式小説", "行動を選択してください。")
                return
            target_id = self.target_map.get(target_var.get())
            result = self.app.run_player_turn(
                player_entity_id=self.player_entity_id,
                action_type=str(option["action_type"]),
                target_id=target_id or (str(option["target_id"]) if option.get("target_id") else None),
                autosave=False,
            )
            refresh_actions()
            refresh_view(message=f"選択: {option['action_label']} | turn={result['turn']}")

        def run_auto_turn() -> None:
            assert self.app is not None
            result = self.app.run_turns(turns=1, autosave=False)[0]
            refresh_actions()
            refresh_view(message=f"自動進行 | turn={result['turn']}")

        def save_snapshot() -> None:
            assert self.app is not None
            path = self.app.save(slot_name="slot_01")
            refresh_view(message=f"保存先: {path}")

        ttk.Button(button_frame, text="行動を実行", command=run_player_turn).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="自動進行", command=run_auto_turn).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_frame, text="保存", command=save_snapshot).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(button_frame, text="再描画", command=refresh_view).pack(side=tk.LEFT, padx=(8, 0))

        def sync_detail(*_: object) -> None:
            selected_label = action_var.get()
            item = self.action_map.get(selected_label)
            detail_var.set(str(item.get('choice_detail', '')) if item else '')

        target_combo["values"] = self._build_target_labels(self.app)
        target_combo.bind("<<ComboboxSelected>>", refresh_actions)
        action_combo.bind("<<ComboboxSelected>>", sync_detail)
        mode_combo.bind("<<ComboboxSelected>>", lambda *_: refresh_view())
        refresh_actions()
        refresh_view()
        self.root.mainloop()


InteractiveDesktopRunner = SimulationDesktopRunner
DialogueNovelDesktopApp = SimulationDesktopRunner
