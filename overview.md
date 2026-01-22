## プロジェクト

YouTube Liveの文字起こし

## 環境

docker-compose.yml の utsulog-st サービスでバッチを実行をする
各種ライブラリは Dockerfile に定義されている

## 概要

1. YouTube Liveの録画をmp3に変換: conv_audio.py

- 入力ファイル：環境変数:VIDEOFILES_DIR配下のmp4ファイルを変換する
- 出力ファイル: 環境変数:AUDIOS_DIR配下のmp3ファイル
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
- 行の先頭にアンカーの行番号 0001. を出力する
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
- to_strip.pyで作成したファイルと比較して、行先頭の{04d}- で欠けた行番号の行を補完する
- 入力ファイル: {元のbasename}_strip.txt
- 出力ファイル: {元のbasename}_fixed.vtt
    - 出力フォルダは{元のbasename}_fixed.txtと同じ
- 欠けた行が閾値100を超えた場合、処理をスキップ
    - スキップしたことをWARNINGで出力する

6. 文字起こしのバッチ処理: batch_to_vtt.py

- mp3ファイルを一括で文字起こしする
- 引数のフォルダからmp3ファイルを検索する
- to_vtt.pyを呼び出して文字起こしを行う
- 出力ファイル: {元のbasename}.vtt
- すでにvttファイルが存在する場合はスキップする
- oomで止まってしまった場合は、スキップする

7. テキスト抽出のバッチ処理: batch_to_strip.py

- 引数のfromフォルダからvttファイルを検索する
- 引数のtoフォルダにテキスト抽出の結果を出力する
- to_strip.pyを呼び出してテキスト抽出を行う

8. 用語リストの作成: make_wordlist.py

- Ginzaの形態素解析で、名詞のリストを作成する。
- 引数のフォルダからtxtファイルを検索する
- 各ファイルのテキストを結合して、名詞のリストを作成する
    - 名詞以外は除外
    - 一意のリスト
- 出力ファイル: wordlist_all.txt

9. Gemini修正依頼のバッチ処理: batch_generate_content.py

- 引数のfromフォルダから_strip.txtファイルを検索する
- generate_content.pyを呼び出してテキスト抽出を行う
- generate_content.pyの出力をログファイルbatch_generate_content.logに保存する。
    - loggingモジュールを使用する

10. 修正結果をVTTに書き戻す: batch_revert_vtt.py

- 引数のfixedフォルダから_fixed.txtファイルを検索する
    - 検索した_fixed.txtファイルと同名の_strip.txtファイルを検索する
- 引数のvttフォルダから.vttファイルを検索する
    - 検索した_strip.txtファイルと同名の.vttファイルを検索する
- revert_vtt.pyを呼び出してVTTファイルを書き戻す
    - original_vtt: 検索したvttファイル
    - fixed_txt: 検索した_fixed.txtファイル
    - strip_txt: 検索した_strip.txtファイル
- 出力ファイル: {元のbasename}_fixed.vtt
- 出力をログファイルbatch_revert_vtt.logに保存する。
    - loggingモジュールを使用する

11. prepare_mv_videos.py

- sambaネットワークフォルダから動画ファイルをVIDEOFILES_DIRにコピーする
    - コピー元: \miniutsuro\share\utsulog-data\videofiles
    - コピー先: VIDEOFILES_DIR
    - コピーするファイル名: *.mp4
    - コピー先にファイルが存在する場合はスキップする
