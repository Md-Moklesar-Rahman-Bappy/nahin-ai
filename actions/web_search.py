#web_search.py
import json
import sys
import threading
import time
from pathlib import Path

# ── Gemini grounding quota circuit breaker ────────────────────────────────────
# The google_search grounding tool has its own small quota, separate from plain
# generation.  Once it is spent every call returns 429 — so retrying it at the
# top of every search only adds a dead round-trip before the DDG fallback runs.
# After a quota error, skip Gemini entirely for a cooldown period.
_QUOTA_COOLDOWN_SEC  = 900          # 15 minutes
_quota_blocked_until = 0.0
_quota_lock          = threading.Lock()


def _gemini_available() -> bool:
    with _quota_lock:
        return time.monotonic() >= _quota_blocked_until


def _note_gemini_error(exc: Exception) -> None:
    """Trip the breaker when the error is a quota / rate-limit rejection."""
    global _quota_blocked_until
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        with _quota_lock:
            already = time.monotonic() < _quota_blocked_until
            _quota_blocked_until = time.monotonic() + _QUOTA_COOLDOWN_SEC
        if not already:
            print(
                "[WebSearch] Gemini grounding quota exhausted — skipping it for "
                f"{_QUOTA_COOLDOWN_SEC // 60} min and serving results from DDG."
            )


class _QuotaCooldown(RuntimeError):
    """Raised instead of calling Gemini while the quota breaker is open."""


def _log_gemini_failure(context: str, exc: Exception) -> None:
    """Log a Gemini failure — silently when it is just the expected cooldown."""
    if isinstance(exc, _QuotaCooldown):
        return          # announced once when the breaker tripped; not a warning
    print(f"[WebSearch] \u26a0\ufe0f {context} failed ({exc}) — using DDG instead")


def _run_bounded(fn, timeout: float, label: str = "task"):
    """Run fn() in a daemon thread; return its result, or None if it overruns."""
    box = [None]

    def _run():
        try:
            box[0] = fn()
        except Exception as e:
            _log_gemini_failure(label, e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        print(f"[WebSearch] {label} exceeded {timeout:.0f}s — moving on")
    return box[0]

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = _get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _gemini_search(query: str) -> str:
    if not _gemini_available():
        raise _QuotaCooldown("Gemini grounding is in quota cooldown")

    from core import gemini

    # Grounded search reads a live page, so it gets a longer deadline than the
    # default — but it still HAS one, and it still walks the fallback ladder.
    try:
        response = gemini.call(query, tier=gemini.SEARCH,
                               config={"tools": [{"google_search": {}}]},
                               timeout_ms=30_000)
        if response is None:
            raise RuntimeError("every Gemini model on the ladder failed")
    except Exception as e:
        _note_gemini_error(e)
        raise

    text = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text += part.text

    text = text.strip()
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return text


def _get_ddgs():
    """
    Returns the DDGS class.  The package was renamed duckduckgo-search -> ddgs;
    the legacy package's endpoints are now rejected by DuckDuckGo (news() gets a
    403 Ratelimit, text() silently returns zero results), so warn loudly if we
    end up on it instead of failing in silence.
    """
    try:
        from ddgs import DDGS
        return DDGS
    except ImportError:
        from duckduckgo_search import DDGS
        print(
            "[WebSearch] ⚠️ Using the deprecated 'duckduckgo-search' package — "
            "DuckDuckGo blocks its endpoints, so every search will come back "
            "empty.  Fix with:  pip install -U ddgs"
        )
        return DDGS


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    DDGS = _get_ddgs()
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title":   r.get("title",  ""),
                    "snippet": r.get("body",   ""),
                    "url":     r.get("href",   ""),
                })
    except Exception as e:
        print(f"[WebSearch] ⚠️ DDG text() failed: {e}")
    return results


def _ddg_news(query: str, max_results: int = 8) -> list[dict]:
    """DDG news search — returns actual articles, not website homepages."""
    DDGS = _get_ddgs()
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append({
                    "title":   r.get("title",  ""),
                    "snippet": r.get("body",   ""),
                    "url":     r.get("url",    ""),
                    "source":  r.get("source", ""),
                })
    except Exception as e:
        print(f"[WebSearch] ⚠️ DDG news() failed ({e}) — falling back to text search")
    # Also covers the legacy-package case, where news() returns an empty list
    # instead of raising.
    if not results:
        results = _ddg_search(query, max_results=max_results)
    return results


def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        if r.get("title"):   lines.append(f"{i}. {r['title']}")
        if r.get("snippet"): lines.append(f"   {r['snippet']}")
        if r.get("url"):     lines.append(f"   Source: {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()


# Prioritized Bangladesh news sources
_BD_SOURCES = {
    "prothom alo", "the daily star", "dhaka tribune", "bdnews24", "bdnews",
    "jugantor", "kaler kantho", "ittefaq", "samakal", "bangladesh",
    "bangla", "bd", "bangladesh politics", "bangladesh economy",
    "bangladesh technology", "bangladesh education", "bangladesh weather",
    "bangladesh government", "bangladesh public safety",
}

# Excluded categories (global only)
_EXCLUDED_KEYWORDS = {
    "us celebrity", "hollywood gossip", "celebrity gossip",
    "foreign entertainment", "us entertainment", "hollywood",
    "celebrity", "gossip", "entertainment news",
}


def _is_country_specific(query: str) -> bool:
    if not query:
        return False
    q = query.lower()
    _COUNTRY_HINTS = [
        " in ", " from ", " about ", "in us", "in usa", "in america", "in uk",
        "in britain", "in england", "in china", "in japan", "in india",
        "in pakistan", "in russia", "in france", "in germany", "in korea",
        "in south korea", "in australia", "in canada", "in brazil",
        "in turkey", "in egypt", "in uae", "in saudi", "in iran", "in iraq",
        "us news", "usa news", "america news", "uk news", "britain news",
        "china news", "japan news", "india news", "pakistan news",
        "russia news", "france news", "germany news", "korea news",
        "south korea news", "australia news", "canada news", "brazil news",
        "turkey news", "egypt news", "uae news", "saudi news", "iran news",
        "iraq news", "london", "washington", "beijing", "tokyo", "delhi",
        "islamabad", "moscow", "paris", "berlin", "seoul", "sydney",
        "ottawa", "brasilia", "ankara", "cairo", "dubai", "riyadh",
        "tehran", "baghdad", "new york", "los angeles",
        "san francisco", "chicago", "houston", "phoenix", "philadelphia",
        "toronto", "vancouver", "melbourne", "sydney", "auckland",
        "manchester", "birmingham", "glasgow", "edinburgh",
        "lombardy", "bavaria", "castile", "andalusia", "provence",
        "rhineland", "saxony", "bavaria", "tyrol", "veneto",
        "tokyo", "osaka", "kyoto", "nagoya", "fukuoka",
        "mumbai", "delhi", "bangalore", "hyderabad", "ahmedabad",
        "karachi", "lahore", "rawalpindi", "faisalabad",
        "beijing", "shanghai", "guangzhou", "shenzhen", "chengdu",
        "seoul", "busan", "incheon", "daegu", "daejeon",
        "canberra", "sydney", "melbourne", "brisbane", "perth",
        "sao paulo", "rio de janeiro", "brasilia", "salvador", "curitiba",
    ]
    for hint in _COUNTRY_HINTS:
        if hint in q:
            return True
    _COUNTRY_NAMES = [
        "united states", "united kingdom", "great britain", "russian federation",
        "federal republic", "people's republic", "republic of", "democratic",
    ]
    for name in _COUNTRY_NAMES:
        if name in q:
            return True
    return False


def _is_bangladesh_relevant(title: str, snippet: str = "") -> bool:
    text = (title + " " + snippet).lower()
    bd_refs = ["bangladesh", "bangla", "bd ", "prothom", "daily star",
               "dhaka tribune", "bdnews", "jugantor", "kaler kantho",
               "ittefaq", "samakal", "bangladesh politics",
               "bangladesh economy", "bangladesh technology",
               "bangladesh education", "bangladesh weather",
               "bangladesh government", "bangladesh public safety"]
    has_bd = any(r in text for r in bd_refs)
    excluded = any(ex in text for ex in _EXCLUDED_KEYWORDS)
    return has_bd and not excluded


def _format_news(query: str, results: list[dict]) -> str:
    if not results:
        return f"No news found for: {query}"

    country_specific = _is_country_specific(query)

    if country_specific:
        # User asked about a specific country — show all relevant results
        lines = [f"Latest news: {query}\n"]
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            if not title:
                continue
            src = f"  [{r['source']}]" if r.get("source") else ""
            lines.append(f"{i}. {title}{src}")
            if r.get("snippet"):
                snippet_clean = r["snippet"][:140]
                lines.append(f"   {snippet_clean}")
            if r.get("url"):
                lines.append(f"   {r['url']}")
            lines.append("")
        return "\n".join(lines).strip()

    # Filter for Bangladesh relevance, exclude unwanted categories
    filtered = []
    for r in results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        if _is_bangladesh_relevant(title, snippet):
            filtered.append(r)
    # If fewer than 5 Bangladesh items exist, include major international news
    if len(filtered) < 5:
        for r in results:
            if r not in filtered:
                filtered.append(r)
        # Limit to max 8 total, with Bangladesh items first
        filtered = filtered[:8]

    lines = [f"Latest Bangladesh news: {query}\n"]
    for i, r in enumerate(filtered, 1):
        title = r.get("title", "")
        if not title:
            continue
        src = f"  [{r['source']}]" if r.get("source") else ""
        lines.append(f"{i}. {title}{src}")
        if r.get("snippet"):
            snippet_clean = r["snippet"][:140]
            # Filter out unwanted snippets
            snippet_lower = snippet_clean.lower()
            if any(ex in snippet_lower for ex in _EXCLUDED_KEYWORDS):
                snippet_clean = "[Excluded category]"
            lines.append(f"   {snippet_clean}")
        if r.get("url"):
            lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()


# ── Briefing helper ────────────────────────────────────────────────────────────

def _gemini_headlines(n: int = 5, query: str = "") -> tuple[list[str], str]:
    """
    Fetches current headlines via Gemini grounded search.
    Default: Bangladesh news. Prioritises Bangladesh politics, economy,
    technology, education, weather alerts, government announcements,
    and public safety. Only includes international news if fewer than
    5 Bangladesh items exist.

    If query specifies another country, fetch that country's headlines instead.
    """
    import re
    from core import gemini

    if _is_country_specific(query):
        headline_prompt = (
            f"Latest news headlines about: {query}. "
            f"Top {n} headlines with one-line summaries. "
            "Include source names."
        )
    else:
        headline_prompt = (
            "Bangladesh news headlines: politics, economy, technology, education, "
            "weather alerts, government announcements, public safety. "
            "Prioritize sources: Prothom Alo, The Daily Star, Dhaka Tribune, "
            "bdnews24, Jugantor, Kaler Kantho, Ittefaq, Samakal. "
            "Exclude US celebrity, Hollywood gossip, foreign entertainment. "
            f"Numbered list: {n} top Bangladesh headlines. If fewer than 5 Bangladesh items, "
            "include major international news."
        )

    response = gemini.call(
        headline_prompt,
        tier=gemini.SEARCH,
        config={"tools": [{"google_search": {}}]},
        timeout_ms=30_000,
    )
    if response is None:
        return [], ""

    raw = ""
    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            raw += part.text

    headlines = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Only accept lines that begin with a number — skips preamble/closing sentences
        if not re.match(r'^[\d]+[.\)\-]', line):
            continue
        clean = re.sub(r'^[\d]+[.\)\-]\s*', '', line)
        clean = re.sub(r'^\*+\s*',          '', clean).strip()
        if clean and len(clean) > 10:
            headlines.append(clean)

    return headlines[:n], raw.strip()


# ── Modes ──────────────────────────────────────────────────────────────────────

def _search(query: str) -> str:
    """Default search — Gemini grounded, DDG fallback."""
    try:
        return _gemini_search(query)
    except Exception as e:
        _log_gemini_failure("Gemini search", e)
        results = _ddg_search(query)
        return _format_ddg(query, results)


def _news(query: str) -> str:
    """
    DDG first, Gemini as backup.

    The old version raced both backends in parallel and kept the first answer.
    That burned one google_search grounding call on *every* news request —
    including the startup briefing — even when DDG had already won the race.
    Grounding has a small quota, so it ran dry after a handful of launches and
    then 429'd for everything else (research/compare), which are the modes that
    actually need a synthesised answer.

    DDG news returns in well under a second and gives raw headlines, which is
    exactly what the briefing wants, so it goes first and Gemini is only touched
    when DDG comes back empty.

    Default country = Bangladesh; default language = Bengali.
    When the user asks about a specific other country, that country's news is
    fetched instead. "latest news" / "news" / "today's news" all mean
    "latest Bangladesh news" unless a country is explicitly specified.
    """
    country_specific = _is_country_specific(query)

    if country_specific:
        gemini_query = (
            f"latest news about: {query}. "
            "Give top headlines, summary of each, and source names."
        )
        ddg_query = query
    else:
        # Default to Bangladesh news for generic queries
        gemini_query = (
            f"latest Bangladesh news: {query}" if query else
            "latest Bangladesh news today: politics, economy, technology, education, "
            "weather alerts, government announcements, public safety. "
            "Prioritize: Prothom Alo, The Daily Star, Dhaka Tribune, bdnews24, "
            "Jugantor, Kaler Kantho, Ittefaq, Samakal. "
            "Exclude: US celebrity, Hollywood gossip, foreign entertainment."
        )
        ddg_query = query if query else "Bangladesh news today"

    def _ddg_attempt() -> str:
        return _format_news(ddg_query, _ddg_news(ddg_query, max_results=8))

    text = _run_bounded(_ddg_attempt, timeout=5.0, label="DDG news")
    if text and len(text) > 60 and not text.startswith("No news found"):
        return text

    text = _run_bounded(
        lambda: _gemini_search(gemini_query), timeout=6.0, label="Gemini news"
    )
    if text and len(text) > 60:
        return text

    return f"No news found for: {query}"


def _research(query: str) -> str:
    """
    Deep dive — asks Gemini for a comprehensive answer with context.
    Falls back to a wider DDG fetch.
    """
    research_query = (
        f"Comprehensive, detailed explanation of: {query}. "
        "Include background context, key facts, current state, and important nuances."
    )
    try:
        return _gemini_search(research_query)
    except Exception as e:
        _log_gemini_failure("Gemini research", e)
        results = _ddg_search(query, max_results=10)
        return _format_ddg(query, results)


def _price(query: str) -> str:
    """Product price lookup — searches for current market prices."""
    price_query = f"current price of {query} — how much does it cost today"
    try:
        return _gemini_search(price_query)
    except Exception as e:
        _log_gemini_failure("Gemini price", e)
        results = _ddg_search(f"{query} price buy", max_results=6)
        return _format_ddg(query, results)


def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Compare {', '.join(items)} in terms of {aspect}. "
        "Give specific facts and data."
    )
    try:
        return _gemini_search(query)
    except Exception as e:
        _log_gemini_failure("Gemini compare", e)

    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"Comparison — {aspect.upper()}", "─" * 40]
    for item in items:
        lines.append(f"\n▸ {item}")
        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  • {r['snippet']}")
            if r.get("url"):
                lines.append(f"    {r['url']}")
    return "\n".join(lines)


# ── Public entry point ─────────────────────────────────────────────────────────

def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Please provide a search query."

    if items and mode not in ("compare",):
        mode = "compare"

    if player:
        player.write_log(f"[Search:{mode}] {query or ', '.join(items)}")

    print(f"[WebSearch] 🔍 mode={mode!r}  query={query!r}")

    try:
        if mode == "compare" and items:
            return _compare(items, aspect)
        if mode == "news":
            return _news(query)
        if mode == "research":
            return _research(query)
        if mode == "price":
            return _price(query)
        return _search(query)

    except Exception as e:
        print(f"[WebSearch] ❌ All backends failed: {e}")
        return f"Search failed: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "web_search",
    "description": "Searches the web. Use for ANY question about current facts, events, prices, or topics — always prefer this over guessing. Modes: 'search' (default), 'news' (latest headlines on a topic), 'research' (deep comprehensive answer), 'price' (product cost lookup), 'compare' (side-by-side comparison of items). Default country = Bangladesh; 'news' and 'latest news' mean Bangladesh news unless another country is specified.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Search query or topic"
            },
            "mode": {
                "type": "STRING",
                "description": "search | news | research | price | compare"
            },
            "items": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                },
                "description": "Items to compare (compare mode)"
            },
            "aspect": {
                "type": "STRING",
                "description": "Comparison aspect: price | specs | reviews | features"
            }
        },
        "required": [
            "query"
        ]
    },
    "handler": web_search,
}
