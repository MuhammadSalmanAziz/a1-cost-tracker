import json
import os
import sys

from dotenv import load_dotenv
from google import genai
from groq import Groq

# Loading the environment variables
load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

# Prices in USD per 1 million tokens,

GEMINI_INPUT_PRICE_PER_M = float(os.getenv("GEMINI_INPUT_PRICE_PER_m"))  
GEMINI_OUTPUT_PRICE_PER_M = float(os.getenv("GEMINI_OUTPUT_PRICE_PER_m"))
GROQ_INPUT_PRICE_PER_M = float(os.getenv("GROQ_INPUT_PRICE_PER_m")  )    
GROQ_OUTPUT_PRICE_PER_M = float(os.getenv("GROQ_OUTPUT_PRICE_PER_m"))

# Total number of prompts to get
MAX_PROMPTS = int(os.getenv("MAX_PROMPT"))


def get_first_prompt():
    """Read the first prompt from the command line. Exit with help if missing."""
    if len(sys.argv) < 2:
        print('Usage: uv run tracker.py "your first prompt"')
        sys.exit(1)
    return " ".join(sys.argv[1:])


def ask_next_prompt(number):
    """Ask the user to type the next prompt. Keeps asking if the input is empty."""
    while True:
        prompt = input(f"\nEnter prompt {number}/{MAX_PROMPTS}: ").strip()
        if prompt:
            return prompt
        print("Prompt cannot be empty.")

# The function is defined to calculate the cost per call
def calculate_cost(input_tokens, output_tokens, input_price_per_m, output_price_per_m):
    """Cost = input_tokens x input_price / 1,000,000 + output_tokens x output_price / 1,000,000"""
    input_cost = input_tokens * input_price_per_m / 1_000_000
    output_cost = output_tokens * output_price_per_m / 1_000_000
    return input_cost + output_cost

# This function is defined to call the first provider : Gemini
def ask_gemini(client, model, prompt):
    """Send one prompt to Gemini and return a result dictionary."""
    resp = client.models.generate_content(model=model, contents=prompt)

    # Token counts come straight from the API's usage data (never estimated)
    input_tokens = resp.usage_metadata.prompt_token_count
    output_tokens = resp.usage_metadata.candidates_token_count

    cost = calculate_cost(
        input_tokens, output_tokens,
        GEMINI_INPUT_PRICE_PER_M, GEMINI_OUTPUT_PRICE_PER_M,
    )
    # This returns the required fields
    return {
        "provider": "gemini",
        "model": model,
        "reply": resp.text or "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": GEMINI_INPUT_PRICE_PER_M,
        "output_price_per_m": GEMINI_OUTPUT_PRICE_PER_M,
        "cost_usd": cost,
    }

# This function is defined to call the Second provider : GROQ
def ask_groq(client, model, prompt):
    """Send one prompt to Groq and return a result dictionary."""
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    input_tokens = resp.usage.prompt_tokens
    output_tokens = resp.usage.completion_tokens

    cost = calculate_cost(
        input_tokens, output_tokens,
        GROQ_INPUT_PRICE_PER_M, GROQ_OUTPUT_PRICE_PER_M,
    )

    return {
        "provider": "groq",
        "model": model,
        "reply": resp.choices[0].message.content or "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": GROQ_INPUT_PRICE_PER_M,
        "output_price_per_m": GROQ_OUTPUT_PRICE_PER_M,
        "cost_usd": cost,
    }

# This function will print the results of prompts.
def print_table(results):
    """Print all results as a simple table with a total at the bottom."""
    print(f"\n{'#':<3}{'provider':<10}{'model':<24}{'input':>8}{'output':>8}{'cost_usd':>14}")
    print("-" * 67)
    total = 0
    for r in results:
        print(
            f"{r['prompt_no']:<3}{r['provider']:<10}{r['model']:<24}"
            f"{r['input_tokens']:>8}{r['output_tokens']:>8}"
            f"{r['cost_usd']:>14.6f}"
        )
        total += r["cost_usd"]
    print("-" * 67)
    print(f"{'TOTAL':<45}{'':>8}{total:>14.6f}")

# This function stores the prompts answer in json form
def save_results(results, filename="results.json"):
    """Save the list of result dictionaries to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)
    print(f"\nSaved {len(results)} results to {filename}")


def main():

    first_prompt = get_first_prompt()

    # Create each API client once and reuse it for every prompt
    gemini_model = os.getenv("GEMINI_MODEL")
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    groq_model = os.getenv("GROQ_MODEL")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    results = []
    for number in range(1, MAX_PROMPTS + 1):
        # Prompt 1 comes from the command line; prompts 2 and 3 are typed in
        if number == 1:
            prompt = first_prompt
        else:
            prompt = ask_next_prompt(number)

        print(f"\n########## Prompt {number}/{MAX_PROMPTS}: {prompt}")

        for result in (
            ask_gemini(gemini_client, gemini_model, prompt),
            ask_groq(groq_client, groq_model, prompt),
        ):
            # Put the prompt info first so the 3 prompts can be told apart in the JSON
            result = {"prompt_no": number, "prompt": prompt, **result}
            results.append(result)
            print(f"\n--- {result['provider']} ({result['model']}) ---")
            print(result["reply"])

    print_table(results)
    save_results(results)


if __name__ == "__main__":
    main()