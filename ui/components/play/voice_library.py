from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class VoiceProfile:
    stance: str
    observation: str
    softener: str
    challenge: str
    confession: str
    support: str
    retreat: str
    help_line: str
    approach_line: str
    wait_line: str
    reaction_guarded: str
    reaction_open: str
    reaction_ambiguous: str


VOICE_LIBRARY: dict[str, VoiceProfile] = {
    'char_001': VoiceProfile(
        stance='感情を押し込める',
        observation='黙って間合いを測る',
        softener='言い切る前に一拍置く',
        challenge='視線を逸らさず核心へ触れる',
        confession='言葉を選びながら本音を差し出す',
        support='押しつけにならない位置で支える',
        retreat='熱が上がる前に線を引く',
        help_line='「悪い、少しだけ支えてくれ」',
        approach_line='「少しだけ、話せるか」',
        wait_line='「今は急がない。まだ見誤りたくない」',
        reaction_guarded='表情を硬くした',
        reaction_open='わずかに力を抜いた',
        reaction_ambiguous='返事の代わりに息をついた',
    ),
    'char_002': VoiceProfile(
        stance='冷静さで傷を隠す',
        observation='余計な感情を見せず見定める',
        softener='棘を薄く包んで差し出す',
        challenge='逃げ道を塞ぐように問いを置く',
        confession='矜持を保ったまま痛みを明かす',
        support='甘さを排して支える',
        retreat='礼節だけを残して引く',
        help_line='「……不本意だけれど、今はあなたの手が必要だわ」',
        approach_line='「少し時間をもらえるかしら」',
        wait_line='「軽率に動く気はないわ。まだ見極めるべきよ」',
        reaction_guarded='睫毛を伏せ、警戒を解かなかった',
        reaction_open='沈黙の奥でわずかに表情を緩めた',
        reaction_ambiguous='目を逸らさず、答えだけを保留した',
    ),
    'char_003': VoiceProfile(
        stance='主導権を握ろうとする',
        observation='相手の隙を探るように眺める',
        softener='柔らかさより先に圧を置く',
        challenge='真正面から押し切る',
        confession='不器用なまま本心を叩きつける',
        support='恩を売る形で手を貸す',
        retreat='負けを認めず一歩だけ退く',
        help_line='「借りを作るのは嫌いだが、今は貸せ」',
        approach_line='「おい、少し付き合え」',
        wait_line='「今はまだだ。無駄打ちはしない」',
        reaction_guarded='顎を引き、対抗心を露わにした',
        reaction_open='不満を残しつつも受け入れた',
        reaction_ambiguous='値踏みするように目を細めた',
    ),
    'char_004': VoiceProfile(
        stance='静かな観察を優先する',
        observation='言葉より先に輪郭を拾う',
        softener='刺激を避けるように言葉を選ぶ',
        challenge='静かな声で逃げ場をなくす',
        confession='ためらいを含んだまま真実へ寄る',
        support='そっと隣に座るように支える',
        retreat='場を乱さないよう一歩離れる',
        help_line='「一人で抱えるには、少し重いの」',
        approach_line='「……少しだけ、聞いてもいい？」',
        wait_line='「今は言葉にしない方が、たぶん正しい」',
        reaction_guarded='息を潜め、相手の続きを待った',
        reaction_open='小さく頷き、受け止める姿勢を見せた',
        reaction_ambiguous='視線を落とし、考えを整えた',
    ),
    'char_005': VoiceProfile(
        stance='余裕の仮面で場を制御する',
        observation='空気の揺れを計算するように見る',
        softener='含みを残して差し出す',
        challenge='笑みのまま圧をかける',
        confession='必要な分だけ切り分けて明かす',
        support='借りを意識させるように支える',
        retreat='主導権を残したまま引く',
        help_line='「今はあなたの手を借りるわ。もちろん、忘れないでね」',
        approach_line='「少し、お話ししましょうか」',
        wait_line='「慌てる必要はないわ。盤面はまだ動くもの」',
        reaction_guarded='口元の笑みだけを残し、内側を閉ざした',
        reaction_open='計算を崩さず、受け入れる余地を見せた',
        reaction_ambiguous='表情を崩さないまま様子を見た',
    ),
    'char_006': VoiceProfile(
        stance='軽やかさで本心を隠す',
        observation='空気に溶けるように探る',
        softener='冗談めかして距離を詰める',
        challenge='笑顔の端で刺す',
        confession='誤魔化しを混ぜながら本音を落とす',
        support='親しげに肩を貸す',
        retreat='明るさを保ったまま引く',
        help_line='「ねえ、今だけは甘えてもいい？」',
        approach_line='「ちょっとだけ、付き合ってくれない？」',
        wait_line='「今は様子見かな。無茶して転ぶのは趣味じゃないし」',
        reaction_guarded='笑みを薄くし、逃げ道を探した',
        reaction_open='肩の力を抜いて笑った',
        reaction_ambiguous='冗談に逃がさず、曖昧に受け止めた',
    ),
    'char_007': VoiceProfile(
        stance='見捨てられまいと縋る',
        observation='不安げに相手の気配へ縋る',
        softener='震えを隠せないまま声を出す',
        challenge='追い詰められて刺々しくなる',
        confession='壊れそうなまま依存を零す',
        support='自分も揺れながら相手に寄る',
        retreat='置いていかれない距離だけ残して引く',
        help_line='「お願い……今は、ひとりにしないで」',
        approach_line='「あの……少しだけ、そばにいて」',
        wait_line='「……まだ、嫌われてないなら。もう少しだけ待つ」',
        reaction_guarded='怯えたように肩をすくめた',
        reaction_open='縋るように息をつき、少しだけ安堵した',
        reaction_ambiguous='返事を求める目だけが残った',
    ),
    'char_008': VoiceProfile(
        stance='場を丸く収めようとする',
        observation='会話の温度差を器用に測る',
        softener='場を和らげる言い回しで入る',
        challenge='人当たりを崩さず核心へ寄る',
        confession='照れを混ぜつつ本音を見せる',
        support='相手の体面を守りながら支える',
        retreat='空気を壊さない形で下がる',
        help_line='「悪い、今はちょっと助けてほしい」',
        approach_line='「少しいい？　空気変えたいんだよね」',
        wait_line='「今は動きすぎないでおくよ。焦ると余計こじれるし」',
        reaction_guarded='愛想は崩さず、距離だけを測った',
        reaction_open='場を和らげるように頷いた',
        reaction_ambiguous='笑みを残しつつ反応を濁した',
    ),
}


def get_voice_profile(entity_id: str) -> VoiceProfile:
    return VOICE_LIBRARY.get(entity_id, VOICE_LIBRARY['char_001'])


VOICE_LINE_LIBRARY: dict[str, dict[str, Callable[[str], str]]] = {
    'char_001': {
        'confession_heavy': lambda target: f'「……{target}にだけは、誤魔化したくない」',
        'confession_calm': lambda target: f'「{target}には、ちゃんと話しておきたい」',
        'support_warm': lambda target: f'「{target}、今は俺が受ける」',
        'support_plain': lambda target: '「必要なら手を貸す」',
        'challenge_sharp': lambda target: f'「{target}、はぐらかすな」',
        'challenge_plain': lambda target: f'「{target}、答えを聞かせてくれ」',
        'retreat': lambda target: '「……今は引く。でも、終わらせる気はない」',
        'observe': lambda target: f'「……{target}の出方を見たい」',
    },
    'char_002': {
        'confession_heavy': lambda target: f'「……{target}にだけは、見苦しいところまで隠せないわ」',
        'confession_calm': lambda target: f'「{target}には、先に伝えておくべきだと思ったの」',
        'support_warm': lambda target: f'「{target}、倒れる前に私を頼りなさい」',
        'support_plain': lambda target: '「必要なら支えるわ。勘違いはしないで」',
        'challenge_sharp': lambda target: f'「{target}、逃げるなら軽蔑するわ」',
        'challenge_plain': lambda target: f'「{target}、曖昧なままにしないで」',
        'retreat': lambda target: '「これ以上は無駄ね。今は退くわ」',
        'observe': lambda target: f'「先に口を開くのは、{target}の方でいいわ」',
    },
    'char_003': {
        'confession_heavy': lambda target: f'「……{target}だから言う。妙な誤解はするな」',
        'confession_calm': lambda target: f'「{target}には話しておく。借りは作りたくない」',
        'support_warm': lambda target: f'「{target}、今は俺の後ろにいろ」',
        'support_plain': lambda target: '「手を貸す。無駄にするなよ」',
        'challenge_sharp': lambda target: f'「{target}、逃げるならその程度だ」',
        'challenge_plain': lambda target: f'「{target}、腹の中を見せろ」',
        'retreat': lambda target: '「今日はここまでだ。次は逃がさない」',
        'observe': lambda target: f'「{target}が何を考えてるか、まず見せてもらう」',
    },
    'char_004': {
        'confession_heavy': lambda target: f'「……{target}になら、少しだけ真実を渡せる気がするの」',
        'confession_calm': lambda target: f'「{target}には、知っていてほしいことがあるの」',
        'support_warm': lambda target: f'「{target}、急がなくていい。ここにいるから」',
        'support_plain': lambda target: '「必要なら、隣で支えるよ」',
        'challenge_sharp': lambda target: f'「{target}、沈黙で隠せる段階は過ぎてる」',
        'challenge_plain': lambda target: f'「{target}、答えを聞かせて」',
        'retreat': lambda target: '「……今は押さない。まだ崩したくないから」',
        'observe': lambda target: f'「まだ、{target}の輪郭を見ていたいの」',
    },
    'char_005': {
        'confession_heavy': lambda target: f'「……{target}には、少しだけ裏側を見せてあげる」',
        'confession_calm': lambda target: f'「{target}には共有しておいた方が得でしょう」',
        'support_warm': lambda target: f'「{target}、借りひとつで支えてあげるわ」',
        'support_plain': lambda target: '「必要なら支えるわ。もちろん、見返りは覚えておいて」',
        'challenge_sharp': lambda target: f'「{target}、その程度の曖昧さで逃げ切れると思わないことね」',
        'challenge_plain': lambda target: f'「{target}、そろそろ本音で話しましょうか」',
        'retreat': lambda target: '「ええ、今日はここまで。盤面はまた作れるもの」',
        'observe': lambda target: f'「急ぐ必要はないわ。{target}の癖くらい見てからで十分」',
    },
    'char_006': {
        'confession_heavy': lambda target: f'「……{target}には、笑ってごまかせないんだよね」',
        'confession_calm': lambda target: f'「{target}には、ちょっと本当のこと話しとこっかな」',
        'support_warm': lambda target: f'「{target}、無理しないで。今は私がついてるから」',
        'support_plain': lambda target: '「必要なら味方するよ。今だけでもね」',
        'challenge_sharp': lambda target: f'「{target}、笑って流せると思ったら間違いだよ」',
        'challenge_plain': lambda target: f'「{target}、ちゃんと聞かせて？」',
        'retreat': lambda target: '「了解、今日は引く。けど忘れたわけじゃないから」',
        'observe': lambda target: f'「ふふ、まずは{target}の本音待ちかな」',
    },
    'char_007': {
        'confession_heavy': lambda target: f'「……{target}だけは、私を置いていかないで」',
        'confession_calm': lambda target: f'「{target}には、嫌われたくないの」',
        'support_warm': lambda target: f'「{target}がつらいなら……私、そばにいる」',
        'support_plain': lambda target: '「うまくできないけど、離れないようにはする」',
        'challenge_sharp': lambda target: f'「{target}、もう誤魔化さないで……怖いの」',
        'challenge_plain': lambda target: f'「{target}、ちゃんと答えて……」',
        'retreat': lambda target: '「……今は下がる。でも、消えたりしないで」',
        'observe': lambda target: f'「……{target}が離れないか、見てる」',
    },
    'char_008': {
        'confession_heavy': lambda target: f'「……{target}には、取り繕っても仕方ないか」',
        'confession_calm': lambda target: f'「{target}には先に言っておきたいんだよね」',
        'support_warm': lambda target: f'「{target}、気張りすぎ。今は俺が受けるよ」',
        'support_plain': lambda target: '「必要なら支えるよ。空気はこっちで何とかする」',
        'challenge_sharp': lambda target: f'「{target}、ここで濁すと余計にまずい」',
        'challenge_plain': lambda target: f'「{target}、今のうちに話しておこう」',
        'retreat': lambda target: '「今日はここまでにしよう。空気が悪くなりすぎる」',
        'observe': lambda target: f'「{target}の空気、先に読ませて」',
    },
}


def render_voice_line(entity_id: str, key: str, target_name: str) -> str:
    callbacks = VOICE_LINE_LIBRARY.get(entity_id, VOICE_LINE_LIBRARY['char_001'])
    callback = callbacks.get(key)
    if callback is None:
        callback = VOICE_LINE_LIBRARY['char_001'][key]
    return callback(target_name)
