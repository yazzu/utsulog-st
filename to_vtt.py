import stable_whisper
import os
import sys

def to_vtt(mp3_file):
    if not os.path.exists(mp3_file):
        print(f"Error: File {mp3_file} not found.")
        return

    model = stable_whisper.load_faster_whisper('large-v3')
    result = model.transcribe(mp3_file,
        language='ja',
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=500, # 無音とみなす最短時間 (デフォルトはもっと短い)
            speech_pad_ms=400, # 音声区間の前後に余白を持たせる（重要）
            threshold=0.5 # 感度 (0.5前後で調整)
        ),
        condition_on_previous_text=False,
        word_timestamps=False,
        repetition_penalty=1.1, # 重複を避ける
        beam_size=5
    )

    basename = os.path.splitext(os.path.basename(mp3_file))[0]
    output_file = f"{basename}.vtt"    
    try:
        result.to_srt_vtt(output_file, word_level=False)
    except AttributeError as e:
        print(f"Failed to find saving methods: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python to_vtt.py <mp3_file>")
    else:
        mp3_file = sys.argv[1]
        to_vtt(mp3_file)

