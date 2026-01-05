import argparse
import logging
from pathlib import Path
from sudachipy import tokenizer
from sudachipy import dictionary

def make_wordlist(input_dir: str, output_file: str):
    """
    指定されたフォルダ内のtxtファイルから名詞を抽出し、リストを作成する。
    SudachiPyのMode C（最長一致）を使用する。
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        logging.error(f"Input directory not found: {input_dir}")
        return

    # SudachiPyの初期化
    try:
        # ja_ginzaインストール済み環境ならコア辞書が入っているはず
        tokenizer_obj = dictionary.Dictionary(dict="core").create()
    except Exception as e:
        logging.warning(f"Failed to load 'core' dictionary, trying default: {e}")
        try:
            tokenizer_obj = dictionary.Dictionary().create()
        except Exception as e2:
             logging.error(f"Failed to create Sudachi tokenizer: {e2}")
             return

    mode = tokenizer.Tokenizer.SplitMode.C
    word_set = set()

    # txtファイルの検索
    files = list(input_path.glob("*.txt"))
    if not files:
        logging.warning(f"No .txt files found in {input_dir}")
        return

    logging.info(f"Found {len(files)} files.")

    for file_path in files:
        logging.info(f"Processing: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    tokens = tokenizer_obj.tokenize(line, mode)
                    
                    for token in tokens:
                        # 品詞を取得 ('名詞', '普通名詞', '一般', '*', '*', '*')
                        pos = token.part_of_speech()
                        
                        # 名詞のみ抽出
                        if pos[0] == "名詞":
                             # output surface form
                            word_set.add(token.surface())

        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")

    # ソートして出力
    sorted_words = sorted(list(word_set))
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for word in sorted_words:
                f.write(f"{word}\n")
        logging.info(f"Successfully wrote {len(sorted_words)} words to {output_file}")
    except Exception as e:
        logging.error(f"Failed to write output file: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Make wordlist from txt files using SudachiPy Mode C.")
    parser.add_argument("input_dir", help="Directory containing input txt files")
    parser.add_argument("--output", default="wordlist_all.txt", help="Output file path")
    
    args = parser.parse_args()
    
    make_wordlist(args.input_dir, args.output)
