# InteractiveNovel_tool

対話式小説シミュレーターです。

## 標準構成

```text
InteractiveNovel_tool/
├─ main.py
├─ config/
├─ core/
│  ├─ logic/
│  ├─ services/
│  ├─ utils/
│  └─ models/
├─ ui/
│  └─ components/
├─ tests/
├─ docs/
├─ logs/
└─ data/
```

補足として、CLI実装は `ui/cli/`、GUI実装は `ui/desktop/` に配置しています。
両者とも `core/logic/` を呼び出す構成です。

## セットアップ

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 起動

```powershell
python main.py --mode cli
python main.py --mode gui
```

## テスト

```powershell
pytest
```
