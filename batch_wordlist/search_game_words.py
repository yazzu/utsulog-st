import os
import re
import sys
from google import genai
from google.genai import types
from google.genai.types import HttpOptions


def sanitize_filename(title):
    """
    Sanitize a game title to create a valid filename.
    Replaces invalid characters with underscores.
    """
    # Replace characters that are invalid in filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', title)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    return sanitized


def search_game_words(input_file='game_title.txt', output_dir='dictionary'):
    """
    Search game-specific terminology using Gemini API with Google Search.
    Results are saved to dictionary/{game_title}.txt for each game.
    Skips games that already have a dictionary file.
    
    Args:
        input_file: Path to the game_title.txt file
        output_dir: Directory to output the extracted game words
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return False
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return False
    
    TIMEOUT_SECONDS = os.environ.get("TIMEOUT_SECONDS")
    if not TIMEOUT_SECONDS:
        print("Warning: TIMEOUT_SECONDS environment variable is not set. Defaulting to 5 minutes.")
        TIMEOUT_SECONDS = 5 * 60 * 1000  # 5 minutes
    
    # Read the game titles
    game_titles = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and line != '不明':  # Skip empty lines and unknown titles
                    game_titles.append(line)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False
    
    if not game_titles:
        print("Error: No game titles found in input file.")
        return False
    
    print(f"Found {len(game_titles)} game titles.")
    
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
    
    # System instruction for game word extraction
    system_instruction = """与えられたゲームのタイトルからゲーム用語を検索して、ゲーム固有の用語を１０個から２０個ピックアップして
## ルール
1.可能な限りGoogle検索を活用してください
2.用語のみを抽出し、余計な装飾や説明は含めないでください
3.主人公・登場人物の名称が一番良いです。
4.一般名詞ではない用語の方がより良いです

出力形式:
- 1行に1用語を出力してください
- 余計な説明や記号は含めないでください
"""
    
    # Enable Google Search tool
    google_search_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
    
    processed_count = 0
    skipped_count = 0
    
    for i, title in enumerate(game_titles):
        # Create output file path
        sanitized_title = sanitize_filename(title)
        output_file = os.path.join(output_dir, f"{sanitized_title}.txt")
        
        # Skip if already processed
        if os.path.exists(output_file):
            print(f"Skipping [{i+1}/{len(game_titles)}]: {title} (already exists)")
            skipped_count += 1
            continue
        
        print(f"Processing [{i+1}/{len(game_titles)}]: {title}")
        
        prompt = f"""## タイトル
{title}"""
        
        try:
            response = client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.5,
                    top_p=0.95,
                    top_k=64,
                    system_instruction=system_instruction,
                    safety_settings=safety_settings,
                    tools=[google_search_tool],
                    response_mime_type="text/plain",
                )
            )
            
            result_text = response.text
            words = [word.strip() for word in result_text.strip().split('\n') if word.strip()]
            
            # Save the results for this game
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in words:
                    f.write(word + '\n')
            
            print(f"  Saved {len(words)} words to {output_file}")
            processed_count += 1
            
        except Exception as e:
            if "timeout" in str(e).lower() or "deadline" in str(e).lower():
                print(f"Error: Request timed out for {title}: {e}")
                continue
            
            print(f"Error processing {title}: {e}")
            continue
    
    print(f"\nCompleted: {processed_count} processed, {skipped_count} skipped")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default usage
        search_game_words()
    elif len(sys.argv) == 2:
        search_game_words(sys.argv[1])
    elif len(sys.argv) == 3:
        search_game_words(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python search_game_words.py [input_file] [output_dir]")
        print("  Default: python search_game_words.py game_title.txt dictionary")
