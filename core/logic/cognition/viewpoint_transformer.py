from __future__ import annotations


class ViewpointTransformer:
    def transform_summary(self, text: str, mode: str) -> str:
        if mode == 'analyst':
            return f'[ANALYST] {text}'
        if mode == 'protagonist':
            return f'[SELF] {text}'
        if mode == 'observer':
            return f'[OBSERVE] {text}'
        return text
