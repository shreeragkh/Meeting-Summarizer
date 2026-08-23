"""Transcript -> structured summary (overview, decisions, action items)."""

import json
from openai import OpenAI
from .config import config
from .utils import chunk_text

_client = OpenAI(api_key=config.OPENAI_API_KEY)

_SUMMARY_PROMPT = """You are an assistant that summarizes meeting transcripts.

From the transcript below, extract:
1. "summary" - a concise 3-5 sentence overview of what was discussed
2. "decisions" - a list of key decisions made (empty list if none)
3. "action_items" - a list of tasks, each with "task", "owner" (or "Unassigned"), and "deadline" (or "Not specified")

Return ONLY valid JSON in this exact format, no extra text:
{{
  "summary": "...",
  "decisions": ["...", "..."],
  "action_items": [
    {{"task": "...", "owner": "...", "deadline": "..."}}
  ]
}}

Transcript:
{transcript}
"""

_MERGE_PROMPT = """Merge these partial meeting summaries into one cohesive result.
Remove duplicate decisions or action items.

Return ONLY valid JSON in this exact format, no extra text:
{{
  "summary": "...",
  "decisions": ["...", "..."],
  "action_items": [
    {{"task": "...", "owner": "...", "deadline": "..."}}
  ]
}}

Partial summaries:
{partial_summaries}
"""


def _call_llm(prompt: str) -> dict:
    response = _client.chat.completions.create(
        model=config.SUMMARY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)


def summarize_transcript(transcript_text: str) -> dict:
    """
    Returns {"summary": str, "decisions": [str], "action_items": [dict]}.
    Long transcripts are chunked, summarized per-chunk, then merged.
    """
    chunks = chunk_text(transcript_text)

    if len(chunks) == 1:
        return _call_llm(_SUMMARY_PROMPT.format(transcript=chunks[0]))

    partial_results = [
        _call_llm(_SUMMARY_PROMPT.format(transcript=chunk)) for chunk in chunks
    ]
    merge_prompt = _MERGE_PROMPT.format(
        partial_summaries=json.dumps(partial_results, indent=2)
    )
    return _call_llm(merge_prompt)