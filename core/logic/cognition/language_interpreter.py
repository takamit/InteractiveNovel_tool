from __future__ import annotations


class LanguageInterpreter:
    def classify_tone(self, action_type: str) -> str:
        mapping = {
            'confront': 'sharp',
            'confide': 'intimate',
            'support': 'gentle',
            'observe': 'neutral',
            'withdraw': 'cold',
            'seek_help': 'vulnerable',
            'approach': 'open',
            'wait': 'ambiguous',
        }
        return mapping.get(action_type, 'neutral')
