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

3. VTTファイルからテキスト抽出: to_strip.py

- PythonでVTTを読み込む: webvtt-py ライブラリなどを使用。
- テキストのみ抽出: タイムスタンプを除外し、テキストをまとめる。
- 行の先頭にアンカーの行番号 L0001. を出力する
- 出力ファイル: {元のbasename}_strip.txt

4. Geminiに修正依頼: generate_content.py

- Geminiに修正依頼: 用語リストと共にテキストを渡し、「修正版」を受け取る。
- model: gemini-3-flash-preview
- 用語リスト: wordlist.txt
- APIキー: GEMINI_API_KEY
- 入力ファイル: {元のbasename}_strip.txt
    - 3000行ごとのブロックに分けて修正依頼する
    - 切れ目が発生するため ２回目以降は 50行をオーバーラップさせる
- 出力ファイル: {元のbasename}_fixed.txt
    - 修正されたテキストを結合して出力する
    - 重複するオーバーラップ部分は削除する
- prompt: prompt.txt
- リクエストタイムアウト: 300秒
- タイムアウトした場合は、処理をスキップする
    - return code: 75

5. 修正結果をVTTに書き戻す: revert_vtt.py

- 修正結果をVTTに書き戻す: 修正されたテキストを元のVTT構造に戻して保存する。
- 入力ファイル: {元のbasename}.vtt
- 入力ファイル: {元のbasename}_fixed.txt
- to_strip.pyで作成したファイルと比較して、行先頭のL{04d}. で欠けた行番号の行を補完する
- 入力ファイル: {元のbasename}_strip.txt
- 出力ファイル: {元のbasename}_fixed.vtt

6. 文字起こしのバッチ処理: batch_to_vtt.py

- mp3ファイルを一括で文字起こしする
- 引数のフォルダからmp3ファイルを検索する
- to_vtt.pyを呼び出して文字起こしを行う
- 出力ファイル: {元のbasename}.vtt
- すでにvttファイルが存在する場合はスキップする
- oomで止まってしまった場合は、スキップする

7. vttファイルを整形するフローをバッチ処理する: batch_fix_vtt.py

- 引数のフォルダからvttファイルを検索する
- temporaryフォルダで作業をする
    - to_strip.py で strip済みファイルを作成する
        - 出力ファイル: {元のbasename}_strip.txt
    - generate_content.pyで修正依頼する
        - 入力ファイル: {元のbasename}_strip.txt
        - 出力ファイル: {元のbasename}_fixed.txt
    - revert_vtt.pyを呼びだしてvttファイルを整形する
        - 入力ファイル: {元のbasename}.vtt
        - 入力ファイル: {元のbasename}_fixed.txt
        - 入力ファイル: {元のbasename}_strip.txt
        - 出力ファイル: {元のbasename}_fixed.vtt
    - 完成したvttファイルを元のフォルダにコピーする
    - 作業用のtemporaryフォルダを削除する

