
# Structured Data Extractor — Nestack Assessment

**Deployment URL:** Not deployed yet. Deploy the private repository using the steps below and replace this line with the live service URL before submission.

A Python/FastAPI backend that accepts unstructured transaction text and uses Gemini to return structured fields with per-field confidence scores and review flags.

## Stack and model choice

- **Python + FastAPI:** concise API implementation, request validation, and automatic OpenAPI docs.
- **Gemini `gemini-2.5-flash-lite`:** the assessment recommends this model; it is a lightweight choice for structured extraction.
- **Google Gen AI SDK:** calls the model with JSON response mode.
- **Post-processing:** normalizes amounts and common date formats, clamps confidence to 0–1, and applies the required review threshold.

## API

### `POST /extract`

Request:
```json
{"text":"Paid ₹ 1,250 to AWS India Pvt Ltd on 12 March 2024. Invoice #INV-2024-0312. Services: cloud compute."}
```

Response shape:
```json
{
  "review_required": false,
  "fields": {
    "vendor_name": {"value": "AWS India Pvt Ltd", "confidence": 0.98, "needs_review": false},
    "amount": {"value": 1250.0, "confidence": 0.99, "needs_review": false},
    "currency": {"value": "INR", "confidence": 0.99, "needs_review": false},
    "date": {"value": "2024-03-12", "confidence": 0.98, "needs_review": false},
    "category": {"value": "software", "confidence": 0.86, "needs_review": false},
    "description": {"value": "Cloud compute services", "confidence": 0.94, "needs_review": false},
    "invoice_id": {"value": "INV-2024-0312", "confidence": 0.99, "needs_review": false}
  }
}
```

The PDF's prose mentions `reviewed_required` once, but its exact response example and later evaluation use **`review_required`**. This implementation follows the exact response example and evaluation wording.

## Setup

Requires Python 3.10+ and a Google AI Studio Gemini API key.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder with your Gemini API key. Do not commit `.env` or share the key.

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
$env:GEMINI_MODEL="gemini-2.5-flash-lite"
py -m uvicorn main:app --reload
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="YOUR_API_KEY"
export GEMINI_MODEL="gemini-2.5-flash-lite"
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to call the endpoint interactively. Health check: `GET http://127.0.0.1:8000/health`.

## Prompt and per-field confidence strategy

The prompt defines every target field and asks the model to return a separate `{value, confidence}` object for each. It tells the model to ground values in the provided text, avoid inventing missing information, score direct facts higher than inferred facts, and lower confidence for missing or ambiguous facts. It specifically prevents resolving relative dates such as “last Tuesday” without a reference date and requests null values with low confidence when data is absent. `temperature=0` reduces variation in extraction.

The API does not trust model confidence blindly: it clamps each score to `[0, 1]`, validates/normalizes field values, and computes `needs_review` separately for every field. A field needs review if confidence is below `0.75` **or its value is null**. `review_required` is true if any field needs review. This null safeguard ensures missing required values cannot be silently auto-saved.

## Run the five assessment inputs and save actual responses to `results.json`

The included `sample_inputs.json` contains the five test inputs. Start the API with a valid API key, then run:

```powershell
py run_samples.py
```

This sends all five requests to the local endpoint and writes their actual API responses to `results.json`.

**Important:** The committed `results.json` included in this starter submission is an illustrative expected-output file, not a verified live Gemini run. Run `run_samples.py` with your own key before submission so it is replaced with the actual responses.

## Deployment

Deploy the app to a Python-capable host (for example, Render or Railway), configure `GEMINI_API_KEY` and `GEMINI_MODEL` as environment variables, and use this start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

After deployment, test `POST /extract`, update the **Deployment URL** at the top of this README, and include the live link in the assessment platform. Do not put API keys in the repository.

## Private GitHub submission checklist

1. Create a **private** repository named `Renuka_Nestack_Submission`.
2. Push the code and confirm the repository visibility is Private (public repositories are disqualified per the assessment instructions).
3. Add these collaborators:
   - `bishal@nestack.com`
   - `sannidhya@nestack.com`
   - `sanjay@nestack.com`
4. Run `py run_samples.py` and commit the refreshed `results.json`.
5. Deploy the app and update the live URL in this README.
6. Upload the complete ZIP and live deployment URL to the assessment platform.

## Files

- `main.py` — FastAPI endpoint and extraction prompt.
- `run_samples.py` — runs all five sample cases against the endpoint.
- `sample_inputs.json` — assessment sample inputs.
- `results.json` — illustrative sample responses; regenerate before submission.
- `requirements.txt` — dependencies.
- `.env.example` — environment variable template.
