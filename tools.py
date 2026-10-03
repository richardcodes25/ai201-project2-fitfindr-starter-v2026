"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

Search never calls the model. The other two call it through generate().

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings

# Letter sizes are whole tokens. "L" must not match "XL", and "S" must not
# match the "S" inside "US".
_LETTER_SIZES = {"XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL"}
_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "in", "of", "with", "under", "size",
}


def _tokens(text: str) -> list[str]:
    """Split on anything that is not a letter or digit. Keep 8.5 as one token."""
    return re.findall(r"\d+\.\d+|[A-Za-z0-9]+", text)


def _keyword_tokens(value) -> set[str]:
    """Lowercased tokens for one listing field. None and empty lists contribute nothing."""
    if value is None:
        return set()
    if isinstance(value, list):
        text = " ".join(str(part) for part in value if part)
    else:
        text = str(value)
    return {token.lower() for token in _tokens(text)}


def _keywords(description: str) -> list[str]:
    words = []
    for word in _keyword_tokens(description):
        if len(word) < 2 or word in _STOPWORDS:
            continue
        words.append(word)
    return words


def _size_matches(requested: str, listing_size: str) -> bool:
    """
    Token match from the Tool Inventory.

    A letter size matches when that token is present, so M matches S/M and
    L does not match XL. A number under 20, or any decimal, is a shoe size
    and must equal that number token. A number 20 or above is a waist, so
    30 and W30 both match W30. One Size matches only a one-size request.
    """
    requested_tokens = [token.upper() for token in _tokens(requested)]
    listing_tokens = [token.upper() for token in _tokens(listing_size)]
    if not requested_tokens:
        return True

    if "ONE" in requested_tokens and "SIZE" in requested_tokens:
        return "ONE" in listing_tokens and "SIZE" in listing_tokens

    letters = [token for token in requested_tokens if token in _LETTER_SIZES]
    if letters:
        return any(token in listing_tokens for token in letters)

    for token in requested_tokens:
        if re.fullmatch(r"\d+\.\d+", token) or (token.isdigit() and float(token) < 20):
            return token in listing_tokens
        if token.isdigit() and float(token) >= 20:
            return f"W{token}" in listing_tokens
        waist = re.fullmatch(r"W(\d+)", token)
        if waist and float(waist.group(1)) >= 20:
            return f"W{waist.group(1)}" in listing_tokens
    return False


def _score(listing: dict, words: list[str]) -> int:
    """One score per keyword: 3 in the title or a style tag, else 2, else 1."""
    title = _keyword_tokens(listing.get("title"))
    tags = _keyword_tokens(listing.get("style_tags"))
    description = _keyword_tokens(listing.get("description"))
    category = _keyword_tokens(listing.get("category"))
    colors = _keyword_tokens(listing.get("colors"))
    brand = _keyword_tokens(listing.get("brand"))
    total = 0
    for word in words:
        if word in title or word in tags:
            total += 3
        elif word in description:
            total += 2
        elif word in category or word in colors or word in brand:
            total += 1
    return total


def _item_facts(new_item: dict) -> str:
    colors = ", ".join(new_item.get("colors") or [])
    tags = ", ".join(new_item.get("style_tags") or [])
    return (
        f"title: {new_item.get('title')}\n"
        f"category: {new_item.get('category')}\n"
        f"size: {new_item.get('size')}\n"
        f"price: {new_item.get('price')}\n"
        f"platform: {new_item.get('platform')}\n"
        f"colors: {colors}\n"
        f"style tags: {tags}\n"
        f"description: {new_item.get('description')}"
    )


def _wardrobe_lines(items: list) -> str:
    lines = []
    for item in items:
        colors = ", ".join(item.get("colors") or [])
        tags = ", ".join(item.get("style_tags") or [])
        notes = item.get("notes") or ""
        lines.append(
            f"- {item.get('name')} | {item.get('category')} | {colors} | {tags} | {notes}"
        )
    return "\n".join(lines)


def _fallback_outfit(new_item: dict) -> str:
    title = new_item.get("title") or "This piece"
    return f"{title} can be styled with simple basics in a close color."


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    words = _keywords(description)
    if not words:
        return []

    matches = []
    for listing in load_listings():
        if max_price is not None and float(listing["price"]) > max_price:
            continue
        if size and not _size_matches(size, str(listing.get("size") or "")):
            continue
        score = _score(listing, words)
        if score <= 0:
            continue
        matches.append((score, float(listing["price"]), listing))

    matches.sort(key=lambda row: (-row[0], row[1]))
    return [listing for _, _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = wardrobe.get("items") or []
    facts = _item_facts(new_item)
    if not items:
        system = (
            "The user owns no clothes yet. Give general styling advice for the "
            "item: one or two outfits made of generic basics. Do not name a "
            "specific garment the user already owns. Reply with sentences, not "
            "a heading."
        )
        prompt = f"Item they are considering:\n{facts}"
    else:
        system = (
            "Suggest one or two outfits that include the thrifted item. Every "
            "outfit must name pieces the user already owns, using the exact "
            "name from the wardrobe list. Do not invent owned pieces. Reply "
            "with sentences, not a heading."
        )
        prompt = (
            f"Item they are considering:\n{facts}\n\n"
            f"Wardrobe, one piece per line as name | category | colors | tags | notes:\n"
            f"{_wardrobe_lines(items)}"
        )
    text = generate(prompt, system=system).strip()
    if not text:
        return _fallback_outfit(new_item)
    return text


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title") or "this item"
    if not outfit or not outfit.strip():
        return f"There is no outfit to post for {title}."

    price = new_item.get("price")
    whole = int(price) if isinstance(price, float) and price.is_integer() else price
    platform = new_item.get("platform") or "the listing"
    system = (
        "Write a social caption someone would post about a thrift find. "
        "Two to four sentences. Sound like a person, not a product page. "
        f"Include the title {title!r} once, the price {whole!r} once, and the "
        f"platform {platform!r} once. Be specific about the vibe."
    )
    prompt = (
        f"Item:\n{_item_facts(new_item)}\n\n"
        f"Outfit to mention:\n{outfit.strip()}"
    )
    text = generate(prompt, system=system).strip()
    if not text:
        return (
            f"Just found {title} for {whole} on {platform}. "
            f"{outfit.strip()}"
        )
    return text
