import os
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from moviepy import AudioFileClip, TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
from app.plugins.base import BasePlugin
from app.context import PipelineContext
from app.constants import BASE_DIR, VOICE_DIR
from app.utils import read_file


# ---- 定数 ----

# デフォルトのフォントパス（システムフォントのフォールバック）
_DEFAULT_FONT = "C:\\Windows\\Fonts\\msgothic.ttc"

# 話者カラーが未設定の場合のデフォルト
_DEFAULT_TEXT_COLOR = "#000000"


# ---- データクラス ----

@dataclass
class SubtitleConfig:
    """settings.yaml の `subtitle` セクションを保持するデータクラス。"""
    font: str
    font_size: int
    bg_color: Tuple[int, int, int]
    width: int
    height: int
    padding_x: int
    silent_duration: float
    speakers: dict

    @classmethod
    def from_config(cls, config: dict) -> "SubtitleConfig":
        """設定辞書から SubtitleConfig を生成する。"""
        subtitle = config.get("subtitle", {})
        font_setting = subtitle.get("font", _DEFAULT_FONT)
        # 相対パスは BASE_DIR 基準の絶対パスに変換
        font = (
            os.path.join(BASE_DIR, font_setting)
            if not os.path.isabs(font_setting)
            else font_setting
        )
        return cls(
            font=font,
            font_size=subtitle.get("font_size", 40),
            bg_color=_hex_to_rgb(subtitle.get("bg_color", "white")),
            width=subtitle.get("width", 1920),
            height=subtitle.get("height", 150),
            padding_x=subtitle.get("padding_x", 250),
            silent_duration=subtitle.get("silent_duration", 0.25),
            speakers=subtitle.get("speakers", {}),
        )


# ---- プラグイン ----

class SubtitleGeneratorPlugin(BasePlugin):
    """
    音声ファイル (.wav) と字幕テキスト (.txt) から
    字幕テロップ付きの動画ファイルをレンダリングするプラグイン。
    """

    def __init__(self, name: str = "subtitle_generator", output_name: str = "subtitle.mp4"):
        super().__init__(name)
        self.output_name = output_name

    def run(self, context: PipelineContext) -> None:
        print(f"[{self.name}] 字幕動画の生成を開始します...")

        cfg = SubtitleConfig.from_config(context.config)
        voice_dir = _resolve_voice_dir(context.config)

        if not os.path.exists(voice_dir):
            print(f"[{self.name}] Error: 音声ディレクトリが見つかりません: {voice_dir}")
            return

        wav_files = sorted(f for f in os.listdir(voice_dir) if f.endswith(".wav"))
        if not wav_files:
            print(f"[{self.name}] Error: WAVファイルが見つかりません: {voice_dir}")
            return

        clips = [
            clip
            for wav_name in wav_files
            if (clip := self._build_clip(wav_name, voice_dir, cfg)) is not None
        ]

        if not clips:
            print(f"[{self.name}] Error: 有効なクリップが1件もありませんでした。")
            return

        output_path = os.path.join(context.output_dir, self.output_name)
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        context.video_output_path = output_path
        print(f"[{self.name}] 字幕動画を保存しました: {output_path}")

    def _build_clip(
        self,
        wav_name: str,
        voice_dir: str,
        cfg: SubtitleConfig,
    ) -> Optional[object]:
        """1件の WAV + TXT ペアから合成クリップを生成して返す。"""
        base_name = os.path.splitext(wav_name)[0]
        txt_path = os.path.join(voice_dir, base_name + ".txt")
        wav_path = os.path.join(voice_dir, wav_name)

        if not os.path.exists(txt_path):
            print(f"[{self.name}] Warning: テキストファイルが見つかりません（スキップ）: {base_name}.txt")
            return None

        text = read_file(txt_path).strip()
        speaker = _extract_speaker(base_name)
        color = _resolve_speaker_color(speaker, cfg.speakers)

        audio = AudioFileClip(wav_path)
        # 文末が句読点の場合のみ無音を付加
        tail_silence = cfg.silent_duration if (text and text[-1] in "、。！？") else 0.0
        clip_duration = audio.duration + tail_silence

        bg_clip = ColorClip(
            size=(cfg.width, cfg.height),
            color=cfg.bg_color,
        ).with_duration(clip_duration)

        txt_clip = TextClip(
            text=text,
            font_size=cfg.font_size,
            color=color,
            font=cfg.font,
            method="caption",
            size=(cfg.width - cfg.padding_x * 2, cfg.height),
            text_align="center",
        ).with_duration(clip_duration).with_position("center")

        clip = CompositeVideoClip([bg_clip, txt_clip]).with_duration(clip_duration).with_audio(audio)
        print(f"[{self.name}] クリップ作成完了: {base_name} ({clip_duration:.2f}s)")
        return clip


# ---- プライベートヘルパー ----

def _resolve_voice_dir(config: dict) -> str:
    """設定辞書から voice_dir の絶対パスを解決する。"""
    voice_dir = config.get("paths", {}).get("voice_dir", VOICE_DIR)
    if not os.path.isabs(voice_dir):
        voice_dir = os.path.join(BASE_DIR, voice_dir)
    return voice_dir


def _extract_speaker(base_name: str) -> str:
    """ファイル名 `{連番}_{話者名}_{識別子}` から話者名を抽出する。"""
    match = re.match(r"^\d{3}_(.*?)_.*$", base_name)
    return match.group(1) if match else "default"


def _resolve_speaker_color(speaker: str, speakers: dict) -> str:
    """話者名と speakers 設定から字幕カラーを返す（部分一致）。"""
    for key, color in speakers.items():
        if key in speaker:
            return color
    return _DEFAULT_TEXT_COLOR


def _hex_to_rgb(color: str) -> Tuple[int, int, int]:
    """
    カラー文字列を (R, G, B) タプルに変換する。
    HEX形式 (#RRGGBB) および代表的な色名に対応。
    """
    _COLOR_NAMES: dict[str, Tuple[int, int, int]] = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red":   (255, 0, 0),
        "blue":  (0, 0, 255),
        "green": (0, 128, 0),
    }
    if isinstance(color, str):
        lower = color.strip().lower()
        if lower in _COLOR_NAMES:
            return _COLOR_NAMES[lower]
        hex_str = lower.lstrip("#")
        if len(hex_str) == 6:
            try:
                r, g, b = (int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                return (r, g, b)
            except ValueError:
                pass
    # フォールバック: 白
    return (255, 255, 255)
