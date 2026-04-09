from __future__ import annotations


class ActionReactionHandler:
    def summarize(self, action_type: str) -> str:
        mapping = {
            'observe': '静かな観察が続いた。',
            'approach': '距離が少し縮まった。',
            'support': '支援が関係を柔らかくした。',
            'withdraw': '一歩引いたことで余白が生まれた。',
            'confront': '対立が空気を尖らせた。',
            'confide': '打ち明け話が関係の温度を変えた。',
            'seek_help': '助けを求める行為が依存と信頼を揺らした。',
            'wait': '決定は先送りされた。',
        }
        return mapping.get(action_type, '変化が起きた。')
