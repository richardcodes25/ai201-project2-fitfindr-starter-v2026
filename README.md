# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

A user asks for a secondhand piece in plain language, like a vintage graphic tee under $30. FitFindr is meant to search the 40 listings, suggest an outfit from their wardrobe, and hand back a fit card. The planning loop is still the starter stub, so that query stops with "The planning loop isn't built yet" and returns no card.

Each listing has `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`. Those are the only fields `search_listings` can filter on. Sizes are not one format (`W30 L30`, `S/M`, `XL (oversized)`, `M`), `price` is a float, and `brand` is often null. A wardrobe item has `id`, `name`, `category`, `colors`, `style_tags`, and optional `notes`. An empty wardrobe is `{"items": []}`.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the 40 listings for items whose text matches a description, after optional size and price filters.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None). None skips that filter. `max_price` is inclusive.
- **Returns:** A list of at most 10 full listing dicts, best match first. Each dict has `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list of str), `size` (str), `condition` (str), `price` (float), `colors` (list of str), `brand` (str or None), and `platform` (str).
- **When it has nothing:** An empty list. Not None, and it does not raise.

Size match is on tokens, not a substring. Split both sizes on anything that is not a letter or a digit, keeping decimals like `8.5` as one token. A letter size (`S`, `M`, `L`, `XL`, and the same with an extra `X`) matches when that token is present, so `M` matches `S/M` and `M/L`, `S` does not match `US 9`, and `L` does not match `XL`. A number under 20, or any number with a decimal, is a shoe size and matches that number token only, so `8` matches `US 8` and not `US 8.5`. A number 20 or above is a waist: look for the token `W` plus that number, so `30` and `W30` both match `W30 L30`. `One Size` matches only a request for one size. The list cap is `config.SEARCH_RESULT_LIMIT`, which is 10.

Score the listings that pass the filters by keyword overlap with `description`. Ignore words shorter than two letters and the words `a`, `an`, `the`, `and`, `or`, `for`, `in`, `of`, `with`, `under`, `size`. A hit in `title` or `style_tags` is 3, a hit in `description` is 2, and a hit in `category`, `colors`, or `brand` is 1. A hit means the keyword equals a token in that field. Drop anything that scores 0. Sort by score descending, then `price` ascending.

### `suggest_outfit`

- **What it does:** Asks the model, through `generate()`, for one or two outfits built around a listing the user is considering.
- **Inputs:** `new_item` (dict, one listing from `search_listings`), `wardrobe` (dict with an `items` key holding a list of wardrobe dicts). Each wardrobe dict has `id` (str), `name` (str), `category` (str), `colors` (list of str), `style_tags` (list of str), and `notes` (str or None).
- **Returns:** A non-empty str naming one or two outfits. When `items` is not empty, each outfit names pieces from that list by `name`.
- **When it has nothing:** Still a non-empty str. An empty `items` list gets general styling advice for `new_item` and names no wardrobe piece. If `generate()` returns blank, return one sentence that names `new_item["title"]`. Do not return `""` and do not raise.

### `create_fit_card`

- **What it does:** Asks the model, through `generate()`, for a short social caption about the find and the outfit.
- **Inputs:** `outfit` (str, the text from `suggest_outfit`), `new_item` (dict, the same listing dict passed to `suggest_outfit`).
- **Returns:** A non-empty str of two to four sentences. It names `new_item["title"]`, `new_item["price"]`, and `new_item["platform"]` once each.
- **When it has nothing:** If `outfit` is empty or only whitespace, do not call the model and do not raise. Return one sentence that says there is no outfit to post and names `new_item["title"]`.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names the description, size, and price that were searched and tells the user to raise the price, drop the size, or change the words, then return the session. Otherwise take the first result and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex and string splitting, not a model call. `under $30` or `under 30` becomes `max_price` (float); if that phrase is missing, `max_price` is None. `size M`, `size US 8`, or `size W30` becomes `size` (str); if that phrase is missing, `size` is None. `description` (str) is the query with those two phrases removed.

**What moves through the session:** `query` (str) goes in first. `parsed` (dict with `description`, `size`, `max_price`) is next. `search_results` (list of listing dicts) is what `search_listings` returned. On the empty-list branch, `error` (str) is set and `selected_item`, `outfit_suggestion`, and `fit_card` stay None. Otherwise `selected_item` (dict) is `search_results[0]`, `outfit_suggestion` (str) is what `suggest_outfit` returned, and `fit_card` (str) is what `create_fit_card` returned.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
