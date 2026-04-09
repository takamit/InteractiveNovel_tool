from __future__ import annotations


class SecretFlagManager:
    def make_flag(self, secret_id: str, visibility: str) -> str:
        return f'{secret_id}:{visibility}'
