"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable  # noqa: F401 — unit 4 catches this

# Regex, not a model call. See README, "How the query is parsed."
_PRICE_RE = re.compile(r"\bunder\s+\$?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_SIZE_RE = re.compile(
    r"\bsize\s+(US\s+\d+(?:\.\d+)?|W\d+|one\s+size|\d+(?:\.\d+)?|[A-Za-z]{1,4}(?:/[A-Za-z]{1,4})?)",
    re.IGNORECASE,
)


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


def _parse_query(query: str) -> dict:
    """Pull description, size, and max_price out of one query. Missing filters are None."""
    price_match = _PRICE_RE.search(query)
    size_match = _SIZE_RE.search(query)
    description = _PRICE_RE.sub(" ", query)
    description = _SIZE_RE.sub(" ", description)
    description = re.sub(r"\s+", " ", description).strip(" ,.-")
    size = None
    if size_match:
        size = re.sub(r"\s+", " ", size_match.group(1)).strip()
    max_price = float(price_match.group(1)) if price_match else None
    return {"description": description, "size": size, "max_price": max_price}


def _no_match_message(parsed: dict) -> str:
    """Name what was searched and what to change. 'No results' is not enough."""
    description = parsed["description"] or "those words"
    size = parsed["size"]
    max_price = parsed["max_price"]
    looked = f"'{description}'"
    if size:
        looked += f" in size {size}"
    else:
        looked += " with no size"
    if max_price is None:
        looked += " and no price limit"
    else:
        shown = int(max_price) if max_price.is_integer() else max_price
        looked += f" under ${shown}"
    changes = []
    if max_price is not None:
        changes.append("raise the price")
    if size:
        changes.append("drop the size")
    changes.append("change the words")
    if len(changes) == 1:
        advice = changes[0]
    elif len(changes) == 2:
        advice = f"{changes[0]} or {changes[1]}"
    else:
        advice = f"{changes[0]}, {changes[1]}, or {changes[2]}"
    return f"Nothing matched {looked}. {advice[0].upper()}{advice[1:]}."


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    rounds = 0

    def _round() -> None:
        nonlocal rounds
        rounds += 1
        trace.check_iterations(rounds)

    _round()
    session["parsed"] = _parse_query(session["query"])

    _round()
    parsed = session["parsed"]
    session["search_results"] = search_listings(
        parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )

    # Branch on the list that was just stored, not on a local variable.
    if len(session["search_results"]) == 0:
        session["error"] = _no_match_message(session["parsed"])
        return session

    _round()
    session["selected_item"] = session["search_results"][0]
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"],
        session["wardrobe"],
    )

    _round()
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"],
        session["selected_item"],
    )
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
