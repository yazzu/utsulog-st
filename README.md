# utsulog-st

YouTube Liveの録画データを文字起こしし、Gemini APIを用いてテキスト補正を行うシステムです。

## 概要

本プロジェクトは、以下のフローで動画データの文字起こしとテキスト補正を行います。

1. **音声変換**: YouTube Liveの録画ファイル(mp4)を音声ファイル(mp3)に変換
2. **文字起こし**: Whisper (stable_whisper) を使用して音声をVTT形式に文字起こし
3. **テキスト抽出**: VTTファイルからテキストのみを抽出し、AI補正用の形式に整形
4. **AI補正**: Gemini APIと用語集(SudachiPyで生成)を使用して誤字脱字や用語を修正
5. **VTT書き戻し**: 修正されたテキストを元のVTTファイルに書き戻し、タイムスタンプを維持したまま字幕データを更新

## 環境构建

Dockerを使用して環境を構築します。`utsulog-st` サービスとして定義されています。

```bash
docker-compose up -d utsulog-st
```

## スクリプト一覧と機能

### 単体処理スクリプト

| スクリプト名 | 機能 | 入力 | 出力 | 備考 |
| --- | --- | --- | --- | --- |
| `conv_audio.py` | 動画をMP3に変換 | `VIDEOFILES_DIR`/*.mp4 | `AUDIOS_DIR`/*.mp3 | 64kbps, Mono, 16kHz |
| `to_vtt.py` | Whisperで文字起こし | MP3ファイル | *.vtt | model: large-v3 |
| `to_strip.py` | テキスト抽出 | *.vtt | *_strip.txt | アンカー(0001.)付与 |
| `generate_content.py` | Geminiでテキスト修正 | *_strip.txt | *_fixed.txt | model: gemini-2.0-flash-exp (or configured) |
| `revert_vtt.py` | 修正結果をVTT反映 | *.vtt, *_fixed.txt, *_strip.txt | *_fixed.vtt | 行整合性チェックあり |

### バッチ処理スクリプト

| スクリプト名 | 機能 | 対象 | ログ/詳細 |
| --- | --- | --- | --- |
| `batch_to_vtt.py` | 一括文字起こし | 指定フォルダ内のMP3 | 既存VTTはスキップ |
| `batch_to_strip.py` | 一括テキスト抽出 | 指定フォルダ内のVTT | - |
| `batch_generate_content.py` | 一括AIテキスト修正 | `*_strip.txt` | `batch_generate_content.log` にログ出力 |
| `batch_revert_vtt.py` | 一括VTT書き戻し | `*_fixed.txt` | `batch_revert_vtt.log` にログ出力 |

### ユーティリティ

- **`make_wordlist.py`**: テキストファイルから名詞を抽出し、用語リスト (`wordlist_all.txt`) を作成します。SudachiPyを使用します。
- **`prepare_mv_videos.py`**: 動画ファイルを指定のネットワークフォルダから `VIDEOFILES_DIR` にコピーします。

## 使用方法 (例)

コンテナ内で各スクリプトを実行します。

```bash
# コンテナに入る
docker-compose exec utsulog-st bash

# バッチ処理の実行 (例: 文字起こし)
python3 batch/batch_to_vtt.py /app/audios /app/vtt
```

各スクリプトの引数や詳細は `overview.md` または各ソースコードを参照してください。

## 設定

環境変数は `.env` ファイルおよび `docker-compose.yml` で管理されています。

- `VIDEOFILES_DIR`: 動画ファイルの保存先
- `AUDIOS_DIR`: 音声ファイルの保存先
- `GEMINI_API_KEY`: Gemini APIを利用するためのキー

## ライセンス

[MIT License](LICENSE) (またはプロジェクトに適用されているライセンス)

### VTT 書き戻しの失敗対象確認

`batch_revert_vtt.py` は修正テキストのディレクトリ（`fixed_dir`）に `revert_vtt_failures.json` を保存します。
失敗した元 VTT・修正テキスト・strip テキスト・出力 VTT の絶対パスと失敗理由を記録します。
一覧は実行ごとに更新され、失敗がなければ空配列になります。

突合できない行がある場合や復元行数が `RESTORED_COUNT_THRESHOLD`（既定値 100）を超える場合、
`revert_vtt.py` は出力 VTT を作成せず、終了コード 1 を返します。
バッチは失敗後も残りのファイルを処理し、1 件でも失敗すると終了コード 1 を返します。
一覧の `fixed_txt` / `strip_txt` を修正して同じバッチコマンドを再実行してください。
既に出力 VTT が存在する対象はスキップされます。

検証: `python -m unittest discover -s batch_st/tests -p 'test_revert_vtt_issue1.py'`
