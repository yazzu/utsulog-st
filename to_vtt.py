import stable_whisper

def main():
    model = stable_whisper.load_faster_whisper('large-v3')
    
    result = model.transcribe('test/7h2YyFjcXY8.mp3',
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
    try:
        result.to_srt_vtt('test/7h2YyFjcXY8.vtt', word_level=False)
    except AttributeError as e:
        print(f"Failed to find saving methods: {e}")

if __name__ == "__main__":
    main()
