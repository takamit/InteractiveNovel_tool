from __future__ import annotations

from typing import Any

from core.logic.runtime.world_state import WorldState
from ui.components.play.voice_library import VoiceProfile, get_voice_profile, render_voice_line


class EmotionDialogueRenderer:
    _ACTION_LABELS = {
        "observe": "様子を見る",
        "approach": "距離を詰める",
        "support": "手を差し伸べる",
        "withdraw": "距離を置く",
        "confront": "真正面からぶつかる",
        "confide": "胸の内を明かす",
        "seek_help": "助けを求める",
        "wait": "まだ動かない",
    }

    def action_label(self, action_type: str) -> str:
        return self._ACTION_LABELS.get(action_type, action_type)

    def choice_prompt(self, state: WorldState, actor_id: str, option: dict[str, Any]) -> str:
        actor = state.entities[actor_id]
        voice = get_voice_profile(actor_id)
        target_id = option.get("target_id")
        target_name = state.entities[target_id].name.full_name if target_id and target_id in state.entities else "相手を絞らない"
        action_label = self.action_label(str(option["action_type"]))
        top_need = str(option.get("top_need") or "unknown")
        emotional_tone = self._emotion_tone(actor)
        motive = self._need_phrase(top_need, voice)
        style_hint = self._style_hint(str(option["action_type"]), voice)
        if target_id:
            return f"{action_label}｜{target_name}｜{emotional_tone}、{style_hint}。{motive}"
        return f"{action_label}｜{emotional_tone}、{style_hint}。{motive}"

    def choice_detail(self, state: WorldState, actor_id: str, option: dict[str, Any]) -> str:
        actor = state.entities[actor_id]
        voice = get_voice_profile(actor_id)
        target_id = option.get("target_id")
        location = state.locations.get(actor.status.current_location_id)
        location_name = location.name if location else actor.status.current_location_id
        target_name = state.entities[target_id].name.full_name if target_id and target_id in state.entities else "周囲"
        privacy = location.privacy_level if location else 0.0
        pressure = location.social_pressure if location else 0.0
        note = "人目は少ない" if privacy >= 60 else ("視線が多い" if pressure >= 60 else "空気はまだ動かせる")
        return f"{location_name}で{target_name}へ。{note}。{voice.stance}姿勢で臨む。"

    def render_actor_line(self, state: WorldState, action: dict[str, Any], *, focal_id: str | None = None, mode: str = "protagonist") -> str:
        actor = state.entities[action["actor_id"]]
        voice = get_voice_profile(actor.id)
        target_id = action.get("target_id")
        target_name = state.entities[target_id].name.full_name if target_id and target_id in state.entities else None
        location = state.locations.get(action["location_id"])
        location_name = location.name if location else action["location_id"]
        opener = self._action_narrative(action["action_type"], voice)
        emotion = self._emotion_color(actor)
        return self._build_sentence(
            actor_name=actor.name.full_name,
            opener=opener,
            emotion=emotion,
            target_name=target_name,
            location_name=location_name,
            mode=mode,
            is_self=focal_id == actor.id,
        )

    def render_reaction_line(self, state: WorldState, action: dict[str, Any], *, focal_id: str | None = None) -> str | None:
        target_id = action.get("target_id")
        if not target_id or target_id not in state.entities:
            return None
        target = state.entities[target_id]
        voice = get_voice_profile(target.id)
        actor = state.entities[action["actor_id"]]
        relation = state.get_relation(action["actor_id"], target_id)
        trust = relation.basic.trust if relation else 0.0
        suspicion = relation.basic.suspicion if relation else 0.0
        if focal_id not in {None, actor.id, target.id}:
            return None
        if suspicion - trust >= 18:
            reaction = voice.reaction_guarded
        elif trust - suspicion >= 18:
            reaction = voice.reaction_open
        else:
            reaction = voice.reaction_ambiguous
        return f"{target.name.full_name}はすぐには答えず、ただ{reaction}。"

    def render_spoken_line(self, state: WorldState, action: dict[str, Any]) -> str | None:
        actor = state.entities[action["actor_id"]]
        target_id = action.get("target_id")
        target_name = state.entities[target_id].name.full_name if target_id and target_id in state.entities else "相手"
        action_type = action["action_type"]
        affection = actor.emotions.affection
        anger = actor.emotions.anger
        fear = actor.emotions.fear
        sadness = actor.emotions.sadness
        pride = actor.inner_profile.pride

        if action_type == "confide":
            key = "confession_heavy" if fear > 40 or sadness > 40 else "confession_calm"
            return render_voice_line(actor.id, key, target_name)
        if action_type == "support":
            key = "support_warm" if affection > 35 else "support_plain"
            return render_voice_line(actor.id, key, target_name)
        if action_type == "confront":
            key = "challenge_sharp" if anger > 35 and pride > 50 else "challenge_plain"
            return render_voice_line(actor.id, key, target_name)
        if action_type == "withdraw":
            return render_voice_line(actor.id, "retreat", target_name)
        if action_type == "seek_help":
            return get_voice_profile(actor.id).help_line
        if action_type == "approach":
            return get_voice_profile(actor.id).approach_line
        if action_type == "observe":
            return render_voice_line(actor.id, "observe", target_name)
        if action_type == "wait":
            return get_voice_profile(actor.id).wait_line
        return None

    def _need_phrase(self, top_need: str, voice: VoiceProfile) -> str:
        mapping = {
            "belonging": f"離されたくない気配がある。{voice.softener}",
            "approval": f"軽く扱われたくない。{voice.stance}",
            "safety": f"これ以上傷を増やしたくない。{voice.retreat}",
            "power": f"主導権は譲れない。{voice.challenge}",
            "freedom": f"縛られる前に動きたい。{voice.observation}",
            "intimacy": f"本音に触れたい。{voice.confession}",
            "health": f"まずは持ちこたえる。{voice.softener}",
        }
        return mapping.get(top_need, f"空気を見て動く。{voice.observation}")

    def _emotion_tone(self, actor: Any) -> str:
        if actor.emotions.anger >= max(actor.emotions.fear, actor.emotions.sadness, actor.emotions.affection, actor.emotions.joy):
            return "棘を隠しきれない"
        if actor.emotions.fear >= max(actor.emotions.anger, actor.emotions.sadness, actor.emotions.affection, actor.emotions.joy):
            return "警戒を解かない"
        if actor.emotions.sadness >= max(actor.emotions.anger, actor.emotions.fear, actor.emotions.affection, actor.emotions.joy):
            return "沈みを抱えた"
        if actor.emotions.affection >= max(actor.emotions.anger, actor.emotions.fear, actor.emotions.sadness, actor.emotions.joy):
            return "柔らかさを残した"
        return "顔色を変えない"

    def _emotion_color(self, actor: Any) -> str:
        if actor.emotions.anger >= 40:
            return "張りつめた"
        if actor.emotions.fear >= 40:
            return "危うい"
        if actor.emotions.sadness >= 40:
            return "沈んだ"
        if actor.emotions.affection >= 35:
            return "やわらかな"
        if actor.emotions.joy >= 35:
            return "少し軽い"
        return "乾いた"

    def _style_hint(self, action_type: str, voice: VoiceProfile) -> str:
        mapping = {
            'observe': voice.observation,
            'approach': voice.softener,
            'support': voice.support,
            'withdraw': voice.retreat,
            'confront': voice.challenge,
            'confide': voice.confession,
            'seek_help': voice.help_line.strip('「」'),
            'wait': voice.wait_line.strip('「」'),
        }
        return mapping.get(action_type, voice.observation)

    def _action_narrative(self, action_type: str, voice: VoiceProfile) -> str:
        mapping = {
            'observe': voice.observation,
            'approach': voice.softener,
            'support': voice.support,
            'withdraw': voice.retreat,
            'confront': voice.challenge,
            'confide': voice.confession,
            'seek_help': '体裁よりも今の安定を選ぶ',
            'wait': 'すぐには動かず、次の波を待つ',
        }
        return mapping.get(action_type, voice.observation)

    def _build_sentence(
        self,
        actor_name: str,
        opener: str,
        emotion: str,
        target_name: str | None,
        location_name: str,
        mode: str,
        is_self: bool,
    ) -> str:
        if mode == "protagonist" and is_self:
            if target_name:
                return f"{location_name}で、私は{target_name}へ向き直る。{emotion}息を整え、{opener}。"
            return f"{location_name}で、私は{emotion}息を整え、{opener}。"
        if mode == "character" and is_self:
            if target_name:
                return f"{actor_name}は{target_name}から視線を逸らさず、{opener}。"
            return f"{actor_name}は{opener}。"
        if target_name:
            return f"{location_name}で、{actor_name}は{emotion}空気をまといながら、{target_name}へ{opener}。"
        return f"{location_name}で、{actor_name}は{emotion}空気をまといながら、{opener}。"
