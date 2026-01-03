import os
import sys
import time
from google import genai
from google.genai import types

def generate_content(input_file, prompt_file='prompt.txt', wordlist_file='wordlist.txt'):
    # Check if files exist
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        return
    if not os.path.exists(prompt_file):
        print(f"Error: Prompt file {prompt_file} not found.")
        return
    
    # wordlist might be optional or empty, but specified in requirements
    wordlist_content = ""
    if os.path.exists(wordlist_file):
        with open(wordlist_file, 'r', encoding='utf-8') as f:
            wordlist_content = f.read().strip()
    else:
        print(f"Warning: Wordlist file {wordlist_file} not found. Proceeding without it.")

    # Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    # Read Input Content
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Read Prompt
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
    except Exception as e:
        print(f"Error reading prompt file: {e}")
        return

    # Construct Final Prompt
    # Inserting wordlist into the prompt if referenced, or appending it.
    # The prompt.txt user provided has sections like "# 用語集".
    # It seems the user intends for us to use the prompt.txt as instructions.
    # We should append the wordlist content if it's not already in the prompt, 
    # OR simpler: concatenate them.
    
    # Strategy:
    # System Instruction / Prompt: prompt_template
    # Content: 
    # Wordlist: ...
    # Text: ...
    
    final_prompt = f"""
{prompt_template}

# 追加用語リスト
{wordlist_content}

# 対象テキスト
{input_text}
"""

    print("Initializing Gemini Client...")
    client = genai.Client(api_key=api_key)

    # ゲーム実況などでは必須の設定
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

    print("Request sent...")
    start_time = time.time()  # 計測開始
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=final_prompt,
            config=types.GenerateContentConfig(
                temperature=1, # Low temperature for correction task
                top_p=0.95,
                top_k=64,
                safety_settings=safety_settings,
                max_output_tokens=8192, # チャンク処理なら8192で十分かつ安全
                response_mime_type="text/plain",
            )
        )
        
        fixed_text = response.text
        
        # Save output
        basename = os.path.splitext(os.path.basename(input_file))[0]
        # input is something_chunks.txt, we want something_fixed.txt
        # if input is 'abc_chunks.txt', basename is 'abc_chunks'.
        # We want 'abc_fixed.txt'.
        if basename.endswith('_chunks'):
             basename = basename[:-7] # remove _chunks
        
        output_file = f"{basename}_fixed.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
            
        print(f"Saved fixed text to {output_file}")

    except Exception as e:
        print(f"Error during generation: {e}")

    finally:
        # 成功・失敗に関わらず時間を表示
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Processing time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_content.py <input_chunks_file> [prompt_file] [wordlist_file]")
    else:
        input_file = sys.argv[1]
        prompt_file = sys.argv[2] if len(sys.argv) > 2 else 'prompt.txt'
        wordlist_file = sys.argv[3] if len(sys.argv) > 3 else 'wordlist.txt'
        generate_content(input_file, prompt_file, wordlist_file)
