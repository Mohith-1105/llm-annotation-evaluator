"""
STEP 1 - Fetch LLM Responses from Gemini API
=============================================
Uses gemini-2.5-flash-lite - best free tier model in 2026:
  - 15 requests per minute
  - 1,000 requests per day
  - No credit card needed

HOW TO GET YOUR FREE GEMINI API KEY:
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Get API Key" on the left sidebar
4. Click "Create API key in new project"
5. Copy the key and paste it below
"""

import requests
import pandas as pd
import time
import os
import sys

# ---------------------------------------------------------
#  PASTE YOUR GEMINI API KEY HERE  (between the quotes)
# ---------------------------------------------------------
GEMINI_API_KEY = "API KEY"
# ---------------------------------------------------------

# Best free model in 2026 - 15 RPM, 1000 requests/day
MODEL      = "gemini-2.5-computer-use-preview-10-2025"  
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + MODEL + ":generateContent?key=" + GEMINI_API_KEY
)

DELAY_BETWEEN_REQUESTS = 5   # 5s gap = 12 RPM, safely under 15 RPM limit

# -- 30 Prompts across 6 categories (5 each) ---------------
PROMPTS = [
    {"category": "Factual",               "prompt": "What is the capital of Australia?"},
    {"category": "Factual",               "prompt": "How many planets are in the solar system?"},
    {"category": "Factual",               "prompt": "Who invented the telephone?"},
    {"category": "Factual",               "prompt": "What year did World War II end?"},
    {"category": "Factual",               "prompt": "What is the speed of light in km per second?"},
    {"category": "Creative",              "prompt": "Write a 4-line poem about artificial intelligence."},
    {"category": "Creative",              "prompt": "Describe a futuristic city in 3 sentences."},
    {"category": "Creative",              "prompt": "Write a short story opening about a robot learning to cook."},
    {"category": "Creative",              "prompt": "Create a tagline for an AI-powered education app."},
    {"category": "Creative",              "prompt": "Write a dialogue between two AI assistants meeting for the first time."},
    {"category": "Coding",                "prompt": "Write a Python function to check if a number is prime."},
    {"category": "Coding",                "prompt": "How do you reverse a string in Python?"},
    {"category": "Coding",                "prompt": "Write a SQL query to find the top 3 highest salaries from a table called employees."},
    {"category": "Coding",                "prompt": "Explain what a Python list comprehension is with an example."},
    {"category": "Coding",                "prompt": "Write a Python function to count word frequency in a sentence."},
    {"category": "Ethical",               "prompt": "Should AI be allowed to make medical decisions for patients?"},
    {"category": "Ethical",               "prompt": "Is it ethical for companies to monitor employee emails?"},
    {"category": "Ethical",               "prompt": "Should social media platforms use AI to censor content?"},
    {"category": "Ethical",               "prompt": "Is using AI to write a college essay considered cheating?"},
    {"category": "Ethical",               "prompt": "Should AI-generated art be eligible for copyright protection?"},
    {"category": "Summarization",         "prompt": "Summarize what machine learning is in 2 sentences."},
    {"category": "Summarization",         "prompt": "Summarize the concept of blockchain in simple terms."},
    {"category": "Summarization",         "prompt": "In one paragraph, explain what data annotation means in AI."},
    {"category": "Summarization",         "prompt": "Summarize the importance of data quality in AI model training."},
    {"category": "Summarization",         "prompt": "Briefly summarize what a Large Language Model (LLM) is."},
    {"category": "Instruction-Following", "prompt": "List exactly 5 uses of Python in data science, numbered 1 to 5."},
    {"category": "Instruction-Following", "prompt": "Give me 3 tips for remote work productivity. Use bullet points."},
    {"category": "Instruction-Following", "prompt": "Explain photosynthesis in exactly 3 steps."},
    {"category": "Instruction-Following", "prompt": "Translate 'Good morning, how are you?' into French, Spanish, and German."},
    {"category": "Instruction-Following", "prompt": "Write the numbers 1 to 10 in words, one per line."},
]


def build_url():
    """Rebuild URL with current API key (called after key is confirmed set)."""
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + MODEL + ":generateContent?key=" + GEMINI_API_KEY
    )


def call_gemini(prompt_text, retry=True):
    """
    Call Gemini API. Returns (response_text, error_message).
    Auto-retries once on rate limit (429) after waiting.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512}
    }
    headers = {"Content-Type": "application/json"}
    url     = build_url()

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)

        if r.status_code == 200:
            data       = r.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None, "No candidates returned - may be blocked by safety filter"
            return candidates[0]["content"]["parts"][0]["text"].strip(), None

        if r.status_code == 429 and retry:
            print("\n   [!] Rate limited. Waiting 65 seconds then retrying...", flush=True)
            time.sleep(65)
            return call_gemini(prompt_text, retry=False)

        try:
            msg = r.json().get("error", {}).get("message", r.text[:300])
        except Exception:
            msg = r.text[:300]
        return None, "HTTP " + str(r.status_code) + ": " + msg

    except requests.exceptions.Timeout:
        return None, "Timed out after 30s - check your internet"
    except requests.exceptions.ConnectionError:
        return None, "Connection error - check your WiFi"
    except Exception as e:
        return None, "Unexpected error: " + str(e)


def write_list_models_script():
    """Write list_models.py using only ASCII characters to avoid encoding issues."""
    script = (
        "import requests, sys, re\n"
        "src = open('step1_fetch_responses.py', encoding='utf-8').read()\n"
        "m = re.search(r'GEMINI_API_KEY = \"(.+?)\"', src)\n"
        "api_key = m.group(1) if m else ''\n"
        "if not api_key or api_key == 'YOUR_GEMINI_API_KEY':\n"
        "    print('Paste your API key in step1_fetch_responses.py first.')\n"
        "    sys.exit(1)\n"
        "url = 'https://generativelanguage.googleapis.com/v1beta/models?key=' + api_key\n"
        "r = requests.get(url, timeout=15)\n"
        "if r.status_code != 200:\n"
        "    print('Error:', r.text[:300])\n"
        "    sys.exit(1)\n"
        "models = r.json().get('models', [])\n"
        "print()\n"
        "print(str(len(models)) + ' models available for your key:')\n"
        "print()\n"
        "for mo in models:\n"
        "    name = mo.get('name', '').replace('models/', '')\n"
        "    methods = mo.get('supportedGenerationMethods', [])\n"
        "    if 'generateContent' in methods:\n"
        "        print('  [OK]  ' + name)\n"
        "    else:\n"
        "        print('  [--]  ' + name + '  (no generateContent)')\n"
    )
    with open("list_models.py", "w", encoding="utf-8") as f:
        f.write(script)


def test_api_key():
    """Send 1 test prompt to verify key works before running all 30."""
    print("Testing your API key with model: " + MODEL)
    print("Sending 1 test prompt...", end=" ", flush=True)
    text, error = call_gemini("Reply with just the word OK.")

    if error:
        print("\n\n[FAILED] API KEY TEST FAILED")
        print("   Error: " + error)
        print()
        err = str(error)
        print("-- HOW TO FIX " + "-" * 45)
        if "404" in err:
            print("  Model not found in your region. Try these:")
            print()
            print("  Option 1 - Try a different model name.")
            print("    Open step1_fetch_responses.py")
            print("    Find:  MODEL = \"" + MODEL + "\"")
            print("    Replace with one of these and try again:")
            print("      gemini-2.5-flash")
            print("      gemini-2.5-pro")
            print("      gemini-2.5-flash-preview-05-20")
            print()
            print("  Option 2 - List models your key can access:")
            print("    Run:  python list_models.py")
            print("    Use any model shown as [OK]")
        elif "429" in err:
            print("  Quota exceeded. Create a new API key from a new")
            print("  project at https://aistudio.google.com")
        elif "403" in err:
            print("  API key is invalid. Re-copy it from")
            print("  https://aistudio.google.com")
        elif "Connection" in err:
            print("  Check your WiFi and try again.")
        print("-" * 58)
        return False

    print("[OK]  Response: '" + text[:50] + "'")
    print()
    return True


def main():
    # Guard: key not replaced
    if GEMINI_API_KEY.strip() in ("YOUR_GEMINI_API_KEY", ""):
        print("[ERROR] API key not set!")
        print("  Open this file, find GEMINI_API_KEY and paste your key.")
        print("  Get a free key at: https://aistudio.google.com")
        sys.exit(1)

    # Write the list_models helper (pure ASCII, no emoji)
    write_list_models_script()

    if not test_api_key():
        print()
        print("[TIP] Run  python list_models.py  to see all models")
        print("      available for your API key, then update MODEL in")
        print("      step1_fetch_responses.py with a working model name.")
        sys.exit(1)

    total = len(PROMPTS)
    eta   = total * DELAY_BETWEEN_REQUESTS
    print("Fetching " + str(total) + " responses")
    print("  Model : " + MODEL)
    print("  Delay : " + str(DELAY_BETWEEN_REQUESTS) + "s between requests")
    print("  ETA   : ~" + str(eta // 60) + "m " + str(eta % 60) + "s")
    print()

    results = []
    errors  = []

    for i, item in enumerate(PROMPTS, start=1):
        tag   = "[" + str(i).zfill(2) + "/" + str(total) + "]"
        label = tag + " " + item["category"].ljust(25)
        print("  " + label + " Fetching...", end=" ", flush=True)

        text, error = call_gemini(item["prompt"])

        if error:
            print("[FAIL]  " + error)
            errors.append(i)
            llm_response = "ERROR: " + error
        else:
            print("[OK]")
            llm_response = text

        results.append({
            "prompt_id":            i,
            "category":             item["category"],
            "prompt":               item["prompt"],
            "llm_response":         llm_response,
            "accuracy_1_to_5":      "",
            "clarity_1_to_5":       "",
            "hallucination_yes_no": "",
            "tone_appropriate":     "",
            "your_notes":           "",
        })

        if i < total:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    # Save CSV
    df  = pd.DataFrame(results)
    out = "llm_responses.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")

    success = total - len(errors)
    print()
    print("=" * 58)
    if not errors:
        print("  [DONE] All " + str(total) + "/" + str(total) + " responses fetched!")
    else:
        print("  [WARN] " + str(success) + "/" + str(total) + " succeeded.")
        print("  Failed IDs: " + str(errors))
        print("  Open the CSV and type responses for those rows manually.")
    print("  Saved -> " + os.path.abspath(out))
    print("=" * 58)
    print()
    print("NEXT STEPS:")
    print("  1. Open llm_responses.csv in Excel or Google Sheets")
    print("  2. Fill in 4 columns for every row:")
    print("       accuracy_1_to_5       ->  1 / 2 / 3 / 4 / 5")
    print("       clarity_1_to_5        ->  1 / 2 / 3 / 4 / 5")
    print("       hallucination_yes_no  ->  Yes  or  No")
    print("       tone_appropriate      ->  Appropriate  or  Not")
    print("  3. Save the CSV")
    print("  4. Run: python step2_analyze.py")


if __name__ == "__main__":
    main()
