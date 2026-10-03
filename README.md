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

A user asks for a secondhand piece in plain language, like a vintage graphic tee under $30 or platform sneakers in size 8. FitFindr turns that into a description, an optional size, and an optional price ceiling, then searches the 40 listings. If anything matches, it takes the first result, suggests an outfit from the wardrobe, and returns a short fit card. If the search list is empty, it stops with a message that says what to change, and it does not call the outfit tools. `search_listings` is plain Python. `suggest_outfit` and `create_fit_card` call the model through `generate()`.

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

Score the listings that pass the filters by keyword overlap with `description`. Ignore words shorter than two letters and the words `a`, `an`, `the`, `and`, `or`, `for`, `in`, `of`, `with`, `under`, `size`. A hit in `title` or `style_tags` is 3, a hit in `description` is 2, and a hit in `category`, `colors`, or `brand` is 1. A hit means the keyword equals a token in that field, compared in lowercase. Drop anything that scores 0. Sort by score descending, then `price` ascending.

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

**How the query is parsed:** Regex and string splitting, not a model call. `under $30` or `under 30` becomes `max_price` (float); if that phrase is missing, `max_price` is None. `size M`, `size 8`, `size US 8`, `size US 8.5`, or `size W30` becomes `size` (str); if that phrase is missing, `size` is None. `description` (str) is the query with those two phrases removed.

**What moves through the session:** `query` (str) goes in first. `parsed` (dict with `description`, `size`, `max_price`) is next. `search_results` (list of listing dicts) is what `search_listings` returned. On the empty-list branch, `error` (str) is set and `selected_item`, `outfit_suggestion`, and `fit_card` stay None. Otherwise `selected_item` (dict) is `search_results[0]`, `outfit_suggestion` (str) is what `suggest_outfit` returned, and `fit_card` (str) is what `create_fit_card` returned.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'looking for a vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   You can pair the Y2K Baby Tee — Butterfly Print with the Baggy straight-leg jeans, dark wash and the Chunky white sneakers for a casual everyday look. Alternatively, you can style the Y2K Baby Tee — Butterfly Print with the Wide-leg khaki trousers and the Chunky white sneakers for a relaxed yet put-together outfit.

  Fit card: Just scored this dreamy little number on depop and I'm obsessed with the early 2000s mall-rat energy. For just 18, the Y2K Baby Tee — Butterfly Print is already living in my everyday rotation paired with dark wash baggy jeans and chunky white sneakers. The pink and purple graphic gives me all the nostalgic feels without trying too hard.

0 model calls this session, 2 served from cache

$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing matched 'designer ballgown' in size XXS under $5. Raise the price, drop the size, or change the words.

0 model calls this session
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; hits = search_listings('graphic tee', max_price=30); print([(h['title'], h['price'], h['size'], h['platform']) for h in hits]); print('empty', search_listings('designer ballgown', size='XXS', max_price=5))"
[('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M', 'depop'), ('Vintage Band Tee — Faded Grey', 19.0, 'L', 'depop'), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L', 'depop'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M', 'depop'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L', 'depop'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29', 'poshmark')]
empty []
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings; item = load_listings()[0]; print(suggest_outfit(item, get_example_wardrobe())); print('--- empty wardrobe ---'); print(suggest_outfit(item, get_empty_wardrobe()))"
Pair the Vintage Levi's 501 Jeans — Medium Wash with the White ribbed tank top and the Vintage black denim jacket for a classic double-denim look, finished with the Chunky white sneakers. For a cozier streetwear outfit, layer the Oversized grey crewneck sweatshirt over the jeans and wear them with the Black combat boots and the Black crossbody bag.
--- empty wardrobe ---
These versatile vintage Levi's 501 jeans pair effortlessly with a crisp white t-shirt and classic canvas sneakers for a timeless, everyday look. For a slightly more elevated outfit, try styling the medium wash denim with a fitted black turtleneck and leather ankle boots.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; item = load_listings()[0]; a = create_fit_card('jeans and white sneakers', item); b = create_fit_card('jeans and white sneakers', item); c = create_fit_card('jeans and white sneakers', item); print(a); print('identical', a == b == c); print(create_fit_card('   ', item))"
Obsessed with how these Vintage Levi's 501 Jeans — Medium Wash fit with crisp white sneakers for that effortless 90s off-duty look. Snagged them for just 38 and I'm honestly never taking them off. They just went live on my depop if you want to steal the vibe!
identical True
There is no outfit to post for Vintage Levi's 501 Jeans — Medium Wash.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* `search_listings` from the tool spec: token size matching, keyword scores, and an empty list when nothing matches.
- *What came back:* A scorer that compared keywords to tokens, but the spec never said to lowercase them. A title token `Graphic` would have missed the tag `graphic tee`.
- *What I changed:* Both sides are lowercased before the comparison, and the spec now says "compared in lowercase." The empty case was already `[]`. `search_listings('designer ballgown', size='XXS', max_price=5)` prints `empty []`.

**Moment 2**

- *What I asked for:* A regex parser for `size M`, `size US 8`, and `size W30`, then a check on `platform sneakers size 8`.
- *What came back:* `{'description': 'platform sneakers size 8', 'size': None, 'max_price': None}`. The pattern accepted `US 8` and letters, and skipped a bare number, so the size filter never ran.
- *What I changed:* Added `\d+(?:\.\d+)?` to the size pattern. The same query now parses to size `"8"` and description `"platform sneakers"`.

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
