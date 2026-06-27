import os
import re
from typing import Any
from moviepy import AudioFileClip, TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
from app.plugins.base import BasePlugin
from app.context import PipelineContext
from app.constants import BASE_DIR, VOICE_DIR
from app.utils import read_file

class SubtitleGeneratorPlugin(BasePlugin):
    """
    音声ファイルと字幕原稿から字幕付きの動画ファイルをレンダリングするプラグイン。
    """
    def __init__(self, name: str = "subtitle_generator", output_name: str = "subtitle.mp4"):
        super().__init__(name)
        self.output_name = output_name

    def run(self, context: PipelineContext) -> None:
        print(f"[{self.name}] Starting subtitle rendering (moviepy mode)...")
        
        # 設定の取得
        subtitle_config = context.config.get("subtitle", {})
        speaker_colors = subtitle_config.get("speakers", {})
        
        font_setting = subtitle_config.get("font", "C:\\Windows\\Fonts\\msgothic.ttc")
        if not os.path.isabs(font_setting):
            # narrative-script/ などのリソースフォルダを直接見る必要があるかもしれないが、
            # pluggable-script側の assets/font/ も想定してBASE_DIR基準にする
            font = os.path.join(BASE_DIR, font_setting)
        else:
            font = font_setting
            
        font_size = subtitle_config.get("font_size", 40)
        width = subtitle_config.get("width", 1920)
        height = subtitle_config.get("height", 150)
        padding_x = subtitle_config.get("padding_x", 250)
        silent_duration = subtitle_config.get("silent_duration", 0.25)
        
        # 音声ソースディレクトリの決定
        voice_dir = context.config.get("paths", {}).get("voice_dir", VOICE_DIR)
        # もし相対パスなら
        if not os.path.isabs(voice_dir):
            voice_dir = os.path.join(BASE_DIR, voice_dir)

        if not os.path.exists(voice_dir):
            print(f"[{self.name}] Error: Voice directory not found: {voice_dir}")
            return

        files = os.listdir(voice_dir)
        wav_files = sorted([f for f in files if f.endswith(".wav")])
        
        if not wav_files:
            print(f"[{self.name}] No wav files found in: {voice_dir}")
            return

        clips = []
        
        for wav_name in wav_files:
            base_name = os.path.splitext(wav_name)[0]
            txt_name = base_name + ".txt"
            txt_path = os.path.join(voice_dir, txt_name)
            wav_path = os.path.join(voice_dir, wav_name)
            
            if not os.path.exists(txt_path):
                print(f"[{self.name}] Warning: Text file not found for voice: {txt_name}")
                continue
                
            # 話者名を抽出
            match = re.match(r"^\d{3}_(.*?)_.*$", base_name)
            speaker = match.group(1) if match else "default"
            
            color = "#000000"
            for s_key, s_color in speaker_colors.items():
                if s_key in speaker:
                    color = s_color
                    break
            
            text = read_file(txt_path).strip()
            audio = AudioFileClip(wav_path)
            
            actual_silent_duration = 0.0
            if text and text[-1] in "、。！？":
                actual_silent_duration = silent_duration
                
            clip_duration = audio.duration + actual_silent_duration
            
            # 背景とテキストの合成
            bg_clip = ColorClip(size=(width, height), color=(255, 255, 255)).with_duration(clip_duration)
            
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
            
            video = CompositeVideoClip([bg_clip, txt_clip]).with_duration(clip_duration).with_audio(audio)
            clips.append(video)
            
            print(f"[{self.name}] Created clip for: {base_name} ({clip_duration:.2f}s)")

        if not clips:
            print(f"[{self.name}] No video clips were created.")
            return

        # 連結
        final_video = concatenate_videoclips(clips, method="compose")
        
        output_path = os.path.join(context.output_dir, self.output_name)
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        context.video_output_path = output_path
        print(f"[{self.name}] Subtitle video saved to: {output_path}")
