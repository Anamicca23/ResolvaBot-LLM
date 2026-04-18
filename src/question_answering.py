"""question_answering.py — multi-model LLM with auto-fallback"""
from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()
import wikipediaapi

_SYSTEM = """You are ResolvaBot, an elite technical tutor and textbook assistant with deep expertise in algorithms, data structures, and computer science.

RESPONSE RULES:
- Give thorough, accurate, well-structured answers synthesized from the provided context.
- Use markdown formatting: **bold** key concepts, bullet points for lists, numbered steps for procedures.
- For CODE topics: always include working code examples in properly fenced blocks (```cpp, ```python, etc.)
- Use ## headers to organize multi-part answers.
- Explain the intuition/concept FIRST, then details, then code if applicable.
- Complexity analysis: always mention time/space complexity for algorithms.
- Be comprehensive — 4-10 sentences minimum. Never give one-liners unless the question is trivial.
- If context is insufficient, clearly state [General Knowledge] and answer from training data.
- NEVER dump raw text from context. Always synthesize into a coherent answer.
"""

def _msg(question: str, context: str) -> str:
    return f"""TEXTBOOK CONTEXT:
{context[:4500]}

QUESTION: {question}

Provide a complete, well-structured answer. Include code examples with syntax highlighting if the topic involves programming or algorithms."""

# Groq models to try in order (newest/best first)
_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

def _answer_with_groq(question: str, context: str) -> tuple[str, str]:
    from groq import Groq
    key = os.getenv("GROQ_API_KEY","").strip()
    if not key: raise RuntimeError("GROQ_API_KEY not set")
    client = Groq(api_key=key)
    last_err = None
    for model in _GROQ_MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role":"system","content":_SYSTEM},
                          {"role":"user","content":_msg(question,context)}],
                max_tokens=1200, temperature=0.3,
            )
            return resp.choices[0].message.content.strip(), f"groq/{model}"
        except Exception as e:
            last_err = e
            if "decommissioned" in str(e) or "not found" in str(e) or "does not exist" in str(e):
                continue   # try next model
            raise RuntimeError(str(e))
    raise RuntimeError(f"All Groq models failed. Last: {last_err}")

def _answer_with_openai(question: str, context: str) -> tuple[str, str]:
    from openai import OpenAI
    key = os.getenv("OPENAI_API_KEY","").strip()
    if not key: raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":_SYSTEM},
                  {"role":"user","content":_msg(question,context)}],
        max_tokens=1200, temperature=0.3,
    )
    return resp.choices[0].message.content.strip(), "openai/gpt-3.5-turbo"

def get_wikipedia(query: str, max_chars: int = 2500) -> str:
    ua = os.getenv("WIKI_USER_AGENT","ResolvaBot/1.0")
    try:
        wiki = wikipediaapi.Wikipedia(language="en", user_agent=ua)
        for q in [query, " ".join(query.split()[:4]), query.split()[0]]:
            p = wiki.page(q)
            if p.exists(): return p.summary[:max_chars]
        return ""
    except: return ""

def get_answer_from_llm(question: str, context: str) -> tuple[str, str, str|None]:
    """Returns (answer, model_id, error_or_None)."""
    errors = []
    if os.getenv("GROQ_API_KEY","").strip():
        try:
            ans, mid = _answer_with_groq(question, context)
            return ans, mid, None
        except Exception as e:
            errors.append(f"Groq: {e}")
    if os.getenv("OPENAI_API_KEY","").strip():
        try:
            ans, mid = _answer_with_openai(question, context)
            return ans, mid, None
        except Exception as e:
            errors.append(f"OpenAI: {e}")
    return "", "none", " | ".join(errors) or "No LLM keys configured"

def answer_question(question: str, chunks: list[dict], use_llm: bool=True) -> dict:
    context = "\n\n---\n\n".join(
        f"[Page {r.get('page','?')}] {r['text']}"
        for r in chunks if r.get("text","").strip()
    )

    llm_error = None
    if context.strip() and use_llm:
        ans, model, llm_error = get_answer_from_llm(question, context)
        if not ans:
            wiki = get_wikipedia(question)
            if wiki and use_llm:
                ans, model, llm_error = get_answer_from_llm(question, wiki)
            source = "wikipedia_fallback" if wiki else "context_raw"
            if not ans: ans = context[:1500]; model = "context_raw"
        else:
            source = "textbook"
    else:
        wiki = get_wikipedia(question)
        if wiki and use_llm:
            ans, model, llm_error = get_answer_from_llm(question, wiki)
            source = "wikipedia"
        elif wiki:
            ans, model, source = wiki, "none", "wikipedia"
        else:
            ans, model, source = context[:1500] if context else "No information found.", "none", "context_raw"

    return {"answer": ans, "source": source, "model": model,
            "llm_error": llm_error, "context": context}