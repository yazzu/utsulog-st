## プロジェクト

YouTube Liveの文字起こし

## 概要

1. YouTube Liveの録画をmp3に変換: conv_audio.py

- オーディオコーデック: MP3
- ビットレート: 64kbps
- チャンネル: 1 (モノラル)
- サンプルレート: 16000 Hz (16kHz)

2. Whisperで文字起こし: to_vtt.py

- vtt形式
- stable_whisper
- Whisperのモデル: large-v3
- 言語: 日本語

3. VTTファイルからテキスト抽出: to_chunk.py

- PythonでVTTを読み込む: webvtt-py ライブラリなどを使用。
- テキストのみ抽出 & チャンク化: タイムスタンプを除外し、テキストを20〜30行ごとのブロック（チャンク）にまとめる。
- 出力ファイル: {元のbasename}_chunks.txt

4. Geminiに修正依頼: generate_content.py

- Geminiに修正依頼: 用語リストと共にテキストを渡し、「修正版」を受け取る。
- model: gemini-3-flash-preview
- 用語リスト: wordlist.txt
- APIキー: GEMINI_API_KEY
- 入力ファイル: {元のbasename}_chunks.txt
- 出力ファイル: {元のbasename}_fixed.txt
- prompt: prompt.txt

5. 修正結果をVTTに書き戻す: revert_vtt.py

- 修正結果をVTTに書き戻す: 修正されたテキストを元のVTT構造に戻して保存する。
- 入力ファイル: {元のbasename}_fixed.txt
- 出力ファイル: {元のbasename}_fixed.vtt
