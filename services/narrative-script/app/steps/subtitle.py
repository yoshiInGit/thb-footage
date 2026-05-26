"""
音声ファイルとテキストデータから字幕映像を生成するステップ。
moviepy 2.x 系に対応。
"""

import os
import re
from typing import Any, Dict, List
from moviepy import AudioFileClip, TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
from app.steps.base import PipelineStep
from app.constants import VOICE_DIR, SUBTITLE_OUT_DIR, BASE_DIR
from app.utils import read_file

class SubtitleStep(PipelineStep):
    """
    input/voice 内の素材から字幕付き動画を生成するクラス。
    """
    def run(self, input_data: Any) -> str:
        print(f"[{self.name}] 字幕映像の生成を開始します (moviepy 2.x mode)...")
        
        # 設定の取得
        subtitle_config = self.config.get("subtitle", {})
        speaker_colors = subtitle_config.get("speakers", {})
        
        font_setting = subtitle_config.get("font", "C:\\Windows\\Fonts\\msgothic.ttc")
        
        # 相対パスの場合はプロジェクトルート基準の絶対パスに変換
        if not os.path.isabs(font_setting):
            font = os.path.join(BASE_DIR, font_setting)
        else:
            font = font_setting
            
        font_size = subtitle_config.get("font_size", 60)
        bg_color = subtitle_config.get("bg_color", "white")
        width = subtitle_config.get("width", 1920)
        height = subtitle_config.get("height", 150)
        padding_x = subtitle_config.get("padding_x", 250)
        silent_duration = subtitle_config.get("silent_duration", 0.15) # デフォルト 0.15s
        
        # 素材のリストアップ
        if not os.path.exists(VOICE_DIR):
            print(f"[{self.name}] Error: 音声ディレクトリが見つかりません: {VOICE_DIR}")
            return ""
            
        files = os.listdir(VOICE_DIR)
        wav_files = sorted([f for f in files if f.endswith(".wav")])
        
        if not wav_files:
            print(f"[{self.name}] 音声ファイルが見つかりません。")
            return ""

        clips = []
        
        for wav_name in wav_files:
            # 対応するテキストファイル名
            base_name = os.path.splitext(wav_name)[0]
            txt_name = base_name + ".txt"
            txt_path = os.path.join(VOICE_DIR, txt_name)
            wav_path = os.path.join(VOICE_DIR, wav_name)
            
            if not os.path.exists(txt_path):
                print(f"[{self.name}] Warning: テキストファイルが見つかりません: {txt_name}")
                continue
                
            # ファイル名から話者名を抽出 (例: 001_アメノちゃん（のーまる）_君なら、)
            match = re.match(r"^\d{3}_(.*?)_.*$", base_name)
            speaker = match.group(1) if match else "default"
            
            # 話者ごとの色（部分一致で検索）
            color = "#000000" # デフォルト
            for s_key, s_color in speaker_colors.items():
                if s_key in speaker:
                    color = s_color
                    break
            
            # コンテンツの読み込み
            text = read_file(txt_path).strip()
            audio = AudioFileClip(wav_path)
            
            # テキストの末尾が句読点（、。！？）の場合のみ無音期間を挿入
            actual_silent_duration = 0.0
            if text and text[-1] in "、。！？":
                actual_silent_duration = silent_duration
                
            # 全体の長さ = 音声の長さ + 無音期間
            clip_duration = audio.duration + actual_silent_duration
            
            # 字幕クリップの作成
            # 背景
            bg_clip = ColorClip(size=(width, height), color=(255, 255, 255)).with_duration(clip_duration)
            
            # テキスト (左右余白を考慮)
            text_w = width - (padding_x * 2)
            txt_clip = TextClip(
                text=text,
                font_size=font_size,
                color=color,
                font=font,
                method='caption',
                size=(text_w, height),
                text_align='center'
            ).with_duration(clip_duration).with_position('center')
            
            # 音声付きクリップの合成 (音声は元の長さのままだが、映像の長さに合わせると末尾が自動的に無音になる)
            video = CompositeVideoClip([bg_clip, txt_clip]).with_duration(clip_duration).with_audio(audio)
            clips.append(video)
            
            print(f"[{self.name}] クリップ作成完了: {base_name} ({clip_duration:.2f}s)")

        if not clips:
            print(f"[{self.name}] クリップが作成されませんでした。")
            return ""

        # 全てのクリップを連結
        final_video = concatenate_videoclips(clips, method="compose")
        
        # 出力
        output_path = os.path.join(self.output_dir, "subtitle.mp4")
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        print(f"[{self.name}] 字幕映像を保存しました: {output_path}")
        return output_path
