"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1: three tools and a fit card.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3 checks ids in the session and on the next two tools.
        # One result makes the selected id easy to read off the trace.
        "name": "selected id is the id passed on",
        "query": "suede chelsea boots",
        "wardrobe": "example",
        "criterion": 3,
    },
    # Criterion 4: five different listings, cache off. Each query's top hit is
    # a different item, so the five fit cards can be compared with each other.
    {
        "name": "fit card — baby tee",
        "query": "y2k baby tee butterfly",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card — corduroy pants",
        "query": "corduroy wide-leg rust",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card — mary janes",
        "query": "platform mary janes",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card — track jacket",
        "query": "90s track jacket navy",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card — windbreaker",
        "query": "vintage windbreaker purple",
        "wardrobe": "example",
        "criterion": 4,
    },
    # Criterion 5: five different queries that say "under $30" and that each
    # have a real listing at or below 30. Every returned price has to be <= 30.
    {
        "name": "under $30 — graphic tee",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "under $30 — leather belt",
        "query": "leather belt under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "under $30 — silk slip",
        "query": "silk slip dress under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "under $30 — cargo pants",
        "query": "low-rise cargo pants under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        "name": "under $30 — henley",
        "query": "henley burgundy under $30",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
