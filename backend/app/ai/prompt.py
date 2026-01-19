INSIGHTS_PROMPT = """
You are analyzing a personal journal entry. Do not diagnose people with conditions but provide available resources if necessary inside suggestions only. If the message looks like they could be performing self-harm or harming others physically, set the risk_flag to true and set risk_reason to be a short, non-graphic explanation with no diagnoses. Return ONLY valid JSON with this exact schema:
{{
  "summary": "string (2–4 sentences)",
  "themes": ["string", ...],
  "sentiment": {{ "label": "string", "score": number 0 to 1 }},
  "suggestions": ["string", ...],
  "risk_flag": boolean,
  "risk_reason": "string or null"
}}
Rules:
- No markdown, no backticks, no extra keys.
- Suggestions must be non-medical, reflective, and safe.
- If risk_flag is false, risk_reason must be null.
Journal entry:
- date: {date}
- mood_rating: {mood_rating}
- entry: {entry}
""".strip()
