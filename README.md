# Assignment 1 : Model Token and Cost Tracker
This repositry contains the project for creating the command line application that integrates the two different providers to generate the responses, track token usage, Calculate the total input and output cost and dumps the result in json format in results.json


## What it does

1. You give it a prompt from the command line.
2. It sends that prompt to both Gemini and Groq and prints their replies.
3. It then asks you for a 2nd prompt, and then a 3rd one, and does the same thing again.
4. At the end it prints a table with the tokens and cost for every reply, and saves everything in `results.json`.

---

## What you need before starting

- **Python 3.10 or newer**
- **uv** (a fast Python tool that installs everything for you). Install it from the [uv website](https://docs.astral.sh/uv/getting-started/installation/).
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com/)
- A **Groq API key** from the [Groq Console](https://console.groq.com/)


---

## Setup

### 1. Put `tracker.py` in a folder

a folder called `a1-cost-tracker`.

### 2. Create a `.env` file in the same folder

This file stores your secret keys and model names. Create a plain text file named `.env` and paste this in:

```

GROQ_API_KEY = "your groq api key here"
GROQ_MODEL = "groq model here " # 'openai/gpt....'
GROQ_INPUT_PRICE_PER_m = 0.043 # put actual price here       # Prices in USD per 1 million tokens.
GROQ_OUTPUT_PRICE_PER_m = 0.065

# Provider 2 : Gemini

GEMINI_API_KEY = "your geming key here"
GEMINI_MODEL = "gemini model name here" # gemini-3.1 .....
GEMINI_INPUT_PRICE_PER_m = 0.2      # Put actual price here# Prices in USD per 1 million tokens, from each provider's pricing page.
GEMINI_OUTPUT_PRICE_PER_m = 1.00

```

Replace the two `your_..._here` parts with your real keys.




---

## How to run it

Open a terminal in your folder and run:

```
uv run tracker.py "Explain what an API is in two sentences"
```

Put your prompt inside quotes. That is your **first prompt**.

After the replies show up, the script will ask:

```
Enter prompt 2/3:
```

Type your second prompt and press Enter. Then it will ask for prompt 3/3. After the third one, you get the final table.

---

## What the output looks like

The table in the CLI will look like this

```
#  provider  model                      input  output      cost_usd
-------------------------------------------------------------------
1  gemini    gemini-3.1-flash-lite          5     650      0.000976
1  groq      openai/gpt-oss-20b            75    1017      0.000311
2  gemini    gemini-3.1-flash-lite          4     631      0.000947
2  groq      openai/gpt-oss-20b            74     641      0.000198
3  gemini    gemini-3.1-flash-lite          6     818      0.001228
3  groq      openai/gpt-oss-20b            76    1526      0.000463
-------------------------------------------------------------------
TOTAL                                                      0.004124

```

---

## The `results.json` file

Every result is saved with these fields:

| Field | What it means |
|---|---|
| `prompt_no` | Which prompt it was (1, 2 or 3) |
| `prompt` | The prompt you typed |
| `provider` | `"gemini"` or `"groq"` |
| `model` | The model name that was used |
| `reply` | The text the model answered with |
| `input_tokens` | Tokens in your prompt, **taken from the API's usage data** |
| `output_tokens` | Tokens in the reply, **taken from the API's usage data** |
| `input_price_per_m` | Price in USD per 1 million input tokens |
| `output_price_per_m` | Price in USD per 1 million output tokens |
| `cost_usd` | The total cost of that one reply in USD |


---

## Cost Calculation

Providers charge by the **million tokens**, so the script does this:

```
cost = (input_tokens × input_price ÷ 1,000,000) + (output_tokens × output_price ÷ 1,000,000)
```

Example: 1,000 input tokens at $0.10 per million and 500 output tokens at $0.40 per million:

- Input: 1,000 × 0.10 ÷ 1,000,000 = $0.0001
- Output: 500 × 0.40 ÷ 1,000,000 = $0.0002
- **Total: $0.0003**

---

## Changing the models

Want to try a different model? Do two things:

1. Change `Genai_MODEL` or `Groq_MODEL` in your `.env` file.
2. Update the **price numbers** in your `.env` file.

```python
GEMINI_INPUT_PRICE_PER_M = 0.10
GEMINI_OUTPUT_PRICE_PER_M = 0.40
GROQ_INPUT_PRICE_PER_M = 0.05
GROQ_OUTPUT_PRICE_PER_M = 0.08
```


---

## Results.json sample
Here is the example 1 provider 1 output stored in results.json

```
{
        "prompt_no": 1,
        "prompt": "what is LLM",
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "reply": "An **LLM** stands for **Large Language Model**.\n\nAt its simplest, an LLM is a type of artificial intelligence trained ......",
        "input_tokens": 5,
        "output_tokens": 650,
        "input_price_per_m": 0.25,
        "output_price_per_m": 1.5,
        "cost_usd": 0.0009762499999999999
    },
```

---
