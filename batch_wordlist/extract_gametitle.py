import os
import sys
import json
from google import genai
from google.genai import types
from google.genai.types import HttpOptions


def extract_gametitle(input_file='videos/videos.ndjson', output_file='game_title.txt'):
    """
    Extract game titles from video titles using Gemini API.
    
    Args:
        input_file: Path to the videos.ndjson file
        output_file: Path to output the extracted game titles
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return False
    
    # Check if output file already exists
    if os.path.exists(output_file):
        print(f"Error: Output file {output_file} already exists.")
        return False
    
    # Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return False
    
    TIMEOUT_SECONDS = os.environ.get("TIMEOUT_SECONDS")
    if not TIMEOUT_SECONDS:
        print("Warning: TIMEOUT_SECONDS environment variable is not set. Defaulting to 5 minutes.")
        TIMEOUT_SECONDS = 5 * 60 * 1000  # 5 minutes
    
    # Read the NDJSON file
    titles = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        if 'title' in obj:
                            titles.append(obj['title'])
                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse JSON line: {e}")
                        continue
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False
    
    if not titles:
        print("Error: No titles found in input file.")
        return False
    
    print(f"Found {len(titles)} video titles.")
    
    # Initialize Gemini Client
    print("Initializing Gemini Client...")
    client = genai.Client(api_key=api_key, http_options=HttpOptions(timeout=TIMEOUT_SECONDS))
    
    # Safety settings
    safety_settings = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_NONE,
        ),
    ]
    
    # System instruction for game title extraction
    system_instruction = """あなたはYouTube動画のタイトルからゲームタイトルを抽出する専門家です。

与えられた動画タイトルのリストから、各タイトルに含まれるゲームタイトルを抽出してください。

ルール:
1. 各入力行に対して、1行で出力してください
2. ゲームタイトルのみを抽出し、余計な装飾や説明は含めないでください
3. ゲームタイトルが見つからない場合は「不明」と出力してください
4. 【】や「」で囲まれた部分にゲームタイトルが含まれることが多いです
5. シリーズ名やサブタイトルがある場合は、完全なゲームタイトルを出力してください
6. 「雑談」「朝活」「歌枠」などの配信カテゴリはゲームタイトルではありません

例:
入力: 【がんばれゴエモン〜宇宙海賊アコギング〜】歯ごたえあり！プレステのゴエモンをやっていくメイド【レトロゲーム】
出力: がんばれゴエモン〜宇宙海賊アコギング〜

入力: 【雑談】今日も一日やりすごそう氷室【朝活】
出力: 不明

入力: 【ロックマンX5】完全初見！ついにX5まできた！世界滅亡の危機がくる！【レトロゲーム】
出力: ロックマンX5

入力: 【歌枠】2025年ありがとう歌枠
出力: 不明
"""
    
    # Create prompt with all titles
    prompt = "\n".join(titles)
    
    print("Sending request to Gemini API...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,  # Lower temperature for more consistent extraction
                top_p=0.95,
                top_k=64,
                system_instruction=system_instruction,
                safety_settings=safety_settings,
                response_mime_type="text/plain",
            )
        )
        
        result_text = response.text
        game_titles = result_text.strip().split('\n')
        
        # Verify the count matches
        if len(game_titles) != len(titles):
            print(f"Warning: Number of game titles ({len(game_titles)}) doesn't match input titles ({len(titles)})")
        
        # Sort and deduplicate the game titles (like sort | uniq)
        unique_game_titles = sorted(set(title.strip() for title in game_titles))
        
        # Save the results
        with open(output_file, 'w', encoding='utf-8') as f:
            for game_title in unique_game_titles:
                f.write(game_title + '\n')
        
        print(f"Saved {len(unique_game_titles)} unique game titles to {output_file} (from {len(game_titles)} total)")
        return True
        
    except Exception as e:
        if "timeout" in str(e).lower() or "deadline" in str(e).lower():
            print(f"Error: Request timed out: {e}")
            sys.exit(75)
        
        print(f"Error during generation: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default usage
        extract_gametitle()
    elif len(sys.argv) == 2:
        extract_gametitle(sys.argv[1])
    elif len(sys.argv) == 3:
        extract_gametitle(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python extract_gametitle.py [input_ndjson_file] [output_file]")
        print("  Default: python extract_gametitle.py videos/videos.ndjson game_title.txt")
