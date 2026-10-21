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

### `compare_price`

- **What it does:** Compares the selected listing's price with the other listings that search just returned.
- **Inputs:** `selected` (dict, one listing), `others` (list of listing dicts).
- **Returns:** A str naming the selected title and its whole-dollar price. If another listing is cheaper, the sentence also names the cheapest of those: its title, whole-dollar price, platform, and how many dollars more the selected item costs.
- **When it has nothing:** If no other listing is cheaper, a str that says the selected item is the cheapest match. Not `""`, and it does not raise.

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

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names the description, size, and price that were searched and tells the user to raise the price, drop the size, or change the words, then return the session. Otherwise take the first result. If another result has a lower price, call `compare_price` and store the sentence in `session["price_comparison"]`, then go to `suggest_outfit`. If nothing is cheaper, leave `price_comparison` as None and go straight to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex and string splitting, not a model call. `under $30` or `under 30` becomes `max_price` (float); if that phrase is missing, `max_price` is None. `size M`, `size 8`, `size US 8`, `size US 8.5`, or `size W30` becomes `size` (str); if that phrase is missing, `size` is None. `description` (str) is the query with those two phrases removed.

**What moves through the session:** `query` (str) goes in first. `parsed` (dict with `description`, `size`, `max_price`) is next. `search_results` (list of listing dicts) is what `search_listings` returned. On the empty-list branch, `error` (str) is set and `selected_item`, `price_comparison`, `outfit_suggestion`, and `fit_card` stay None. Otherwise `selected_item` (dict) is `search_results[0]`. `price_comparison` (str or None) is set only when a cheaper listing is in that list. `outfit_suggestion` (str) is what `suggest_outfit` returned, and `fit_card` (str) is what `create_fit_card` returned. The wardrobe for `suggest_outfit` is the wardrobe passed in, plus any pieces saved in `wardrobe_memory.json` from earlier runs.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'looking for a vintage graphic tee under $30'

  Price:    Y2K Baby Tee — Butterfly Print at 18 costs 6 more than Leather Belt — Brown, Braided at 12 on thredUp.

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

---

## Stretch

Declared before the code below existed.

### Fourth tool: `compare_price`

- **What it does:** Compares the selected listing's price with the other listings that search just returned.
- **Inputs:** `selected` (dict, one listing), `others` (list of listing dicts).
- **Returns:** A str naming the selected title and its whole-dollar price. If another listing in `others` is cheaper, the sentence also names the cheapest of those: its title, whole-dollar price, platform, and how many dollars more the selected item costs.
- **When it has nothing:** If no other listing is cheaper, a str that says the selected item is the cheapest match. Not `""`, and it does not raise.

### Second branch

If `search_results` contains a listing with a lower `price` than `selected_item`, call `compare_price` and store the sentence in `session["price_comparison"]`, then go to `suggest_outfit`. If nothing is cheaper, leave `price_comparison` as None and go straight to `suggest_outfit`. The empty-search stop is unchanged. Both branches live in `agent.py::run_agent`.

### Style memory

After a run that selects an item, save that item into `wardrobe_memory.json`. The next run loads that file and adds those pieces to the wardrobe passed into `suggest_outfit`. A saved piece has notes `saved from a previous search`, and one outfit in the next run names it.

`compare_price` is `tools.py::compare_price`. The second branch and the save both happen in `agent.py::run_agent`. What changed: a matching query can now print a price sentence before the outfit, and the next query's wardrobe includes the item the previous query selected.

The price branch was taken here. Search put a $12 belt in the same result list as the $18 tee, so the loop called `compare_price` before `suggest_outfit`.

```
$ python app.py ask 'looking for a vintage graphic tee under $30'

  Price:    Y2K Baby Tee — Butterfly Print at 18 costs 6 more than Leather Belt — Brown, Braided at 12 on thredUp.

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
```

Style memory, with `wardrobe_memory.json` cleared before the first command. The second outfit names the tee the first run stored.

```
$ python app.py ask 'looking for a vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

$ python app.py ask 'oversized flannel shirt'

  Remembered: Y2K Baby Tee — Butterfly Print

  Price:    Oversized Flannel Shirt — Plaid Red/Black at 22 costs 5 more than Tie-Dye Long Sleeve — Pastel at 17 on depop.

  Found:    Oversized Flannel Shirt — Plaid Red/Black — $22.0 on thredUp

  Outfit:   For a layered 90s grunge streetwear look, wear your Oversized Flannel Shirt — Plaid Red/Black buttoned over the Y2K Baby Tee — Butterfly Print, paired with the Baggy straight-leg jeans, dark wash, and finish the outfit with the Black combat boots.
```

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

`python run_eval.py --label before` wrote `results/run_2026-10-22_0219_before.md` (`run_eval.py::write_report`, cache off, temperature 0.9). Each row below is scored from that file. The loop is `agent.py::run_agent`. Fit cards come from `tools.py::create_fit_card`.

For criteria 1–3, a try is one repeat of that scenario. For criterion 4, a try is one round of the five listings. For criterion 5, a try is one round of the five `under $30` queries. Openings on the model criteria were not the same from try to try.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Full three-tool run returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Empty search stops before suggest_outfit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. Selected id is the id passed on | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit cards keep price, platform, and a unique opening | 5/5 facts, 4/5 unique openings | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. under $30 never returns a price over 30 | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function that produced it. All of it is from `results/run_2026-10-22_0219_before.md`, written by `run_eval.py::write_report`.

**1.** `agent.py::run_agent` on `vintage graphic tee under $30`, try 1. The trace shows search, `suggest_outfit`, and `create_fit_card`. The fit card is from `tools.py::create_fit_card`:

```
[1] search_listings (via MCP)
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results, continue; first id lst_002; prices 18.0, 19.0, 24.0, 26.0, 15.0, 12.0, 14.0, 16.0, 18.0, 20.0
[3] suggest_outfit
      →    new_item id lst_002
[4] create_fit_card
      →    new_item id lst_002

Still recovering from the fact that I only paid 18 for this little pastel dream. I just scored this exact Y2K Baby Tee — Butterfly Print on depop and the pink and purple glitter graphic is giving major 2003 mall-rat energy. Honestly can't wait to grunge it down with an oversized flannel and some beat-up combat boots.
```

**2.** `agent.py::run_agent` on `designer ballgown size XXS under $5`, try 1. The trace stops after search. `suggest_outfit` is not called:

```
- stopped early: yes — Nothing matched 'designer ballgown' in size XXS under $5. Raise the price, drop the size, or change the words.
- selected_item: (none)
- search_results: 0

[1] search_listings (via MCP)
      out: [] (empty)
      →    branch: empty, stopping
```

**3.** `agent.py::run_agent` on `suede chelsea boots`, try 1. The first search id, the selected id, and both `new_item` ids are `lst_028`:

```
- selected_item: Suede Chelsea Boots — Tan ($44.0, poshmark)
- search_results: 1
[1] search_listings (via MCP)
      →    branch: results, continue; first id lst_028; prices 44.0
[2] price branch
      →    branch: skip compare_price; selected id lst_028
[3] suggest_outfit
      →    new_item id lst_028
[4] create_fit_card
      →    new_item id lst_028
```

**4.** `tools.py::create_fit_card`, try 1 of each of the five listings. Each card contains that item's whole-dollar price and platform. The five first sentences are different:

```
Literal heart eyes for this little thrift score I just listed on depop. Snagged this Y2K Baby Tee — Butterfly Print for just 18 and the pastel pink and purple butterfly graphics give off the ultimate nostalgic 2000s mall-rat energy. Throwing it on with some baggy straight-leg jeans and suede chelsea boots for the easiest coffee run fit ever.

Found my ultimate 70s autumn uniform on depop and I am never taking it off. These Corduroy Wide-Leg Pants — Rust were only 32 and they fit like an absolute dream. I’m styling them with an unbuttoned plaid flannel over a butterfly baby tee and my favorite tan Chelsea boots for the coziest, most nostalgic vibe.

Still pinching myself over finding these on depop for just 55! Total 90s mall goth energy, especially paired with an oversized red plaid flannel and dark wash baggy jeans. My inner teenager is screaming.

Finally got my hands on the ultimate retro streetwear piece for just $45 on poshmark. This 90s Track Jacket — Navy/White Stripe looks so good thrown over a little baby tee and wide-leg cords. It’s got that perfect crunchy, lightweight nylon feel that makes it impossible not to wear every single day.

Found the ultimate dad jacket on thredUp and I am never taking it off. This Vintage Windbreaker — Color Block Purple/Teal was only 40 and gives off the best early '90s ski trip energy. I'm totally throwing it on over some rust corduroys and beat-up boots for the weekend.
```

**5.** `agent.py::run_agent`, try 1, in this order: `vintage graphic tee under $30`, `leather belt under $30`, `silk slip dress under $30`, `low-rise cargo pants under $30`, `henley burgundy under $30`. Every list is non-empty and every price is at or below 30:

```
- search_results: 10
      →    branch: results, continue; first id lst_002; prices 18.0, 19.0, 24.0, 26.0, 15.0, 12.0, 14.0, 16.0, 18.0, 20.0

- search_results: 1
      →    branch: results, continue; first id lst_014; prices 12.0

- search_results: 2
      →    branch: results, continue; first id lst_013; prices 30.0, 28.0

- search_results: 2
      →    branch: results, continue; first id lst_011; prices 27.0, 20.0

- search_results: 1
      →    branch: results, continue; first id lst_020; prices 16.0
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
| 1 | A matching query completes all three tools | 4 of 5 | MET | Five tries of `vintage graphic tee under $30` each ran `search_listings`, `suggest_outfit`, and `create_fit_card` and returned a non-empty fit card. Five passes meets a target of 4. |
| 2 | An impossible query stops before `suggest_outfit` | 5 of 5 | MET | Five tries of the ballgown query each stopped on an empty list, told the user to raise the price, drop the size, or change the words, and the trace has no `suggest_outfit` step. |
| 3 | The selected id is the id passed on | 5 of 5 | MET | On all five `suede chelsea boots` tries, `search_results[0]`, `selected_item`, and the `new_item` passed to `suggest_outfit` and `create_fit_card` were `lst_028`. |
| 4 | Fit cards keep the facts and do not share an opening | all 5 have price and platform; at least 4 openings unique | MET | In each of five rounds, every card contained that listing's whole-dollar price and platform, and all five first sentences (text before the first period) were different. |
| 5 | A price ceiling is never broken | 5 of 5 | MET | In each of five rounds, all five `under $30` queries returned a non-empty list and every price was <= 30. The highest price in any list was 30.0. |

**Diagnoses**

Nothing missed. There is no shared failure in a tool, the loop's branch, the session, or the model's output.

The opposite reading that comes closest is criterion 1: the five tries used `vintage graphic tee under $30`, which overlaps a listing title, and the written reason for the target was that a looser phrasing such as "old band shirt" can score zero. That does not flip the verdict. The criterion says a query that matches at least one listing, and this one does. Five of five fit cards against a target of 4 of 5 is MET.

Criteria 2, 3, and 5 ask for 5 of 5 on checks the model cannot sway, and the counts are 5. Criterion 4's uniqueness bar of 4 of 5 was a little soft: every round had 5 distinct openings, so requiring all 5 to differ would still be MET. That softness did not hide a miss.

The criterion I would tighten is criterion 1. Keep the 4-of-5 count, because a model call can still come back blank. Change the query to one that shares little with the title, such as "old band shirt", so a keyword miss can actually show up. I am not revising `criteria.md`. The original line is measurable, and it was met.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path** — `python app.py ask 'vintage graphic tee under $30' --trace`

```
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: results, continue
[2] compare_price
      in:  dict with keys: selected, others
      out: Y2K Baby Tee — Butterfly Print at 18 costs 6 more than Leather Belt — Brown, Braided at 12 on thredUp.
      →    branch: a cheaper listing exists
[3] suggest_outfit
      in:  dict with keys: new_item, wardrobe_items
      out: For a casual Y2K-inspired look, wear the Y2K Baby Tee — Butterfly Print tucked into the Baggy straight-leg jea…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Just scored the ultimate early 2000s piece for only 18 on depop and I am obsessed with the pink and purple col…
```

**Empty search** — `python app.py ask 'designer ballgown size XXS under $5' --trace`

```
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping
```

The agent then said: Nothing matched 'designer ballgown' in size XXS under $5. Raise the price, drop the size, or change the words.

**Failure messages**

Empty search: Nothing matched 'designer ballgown' in size XXS under $5. Raise the price, drop the size, or change the words.

Empty wardrobe (`python app.py ask 'vintage graphic tee under $30' --empty-wardrobe`): Pair this fitted graphic baby tee with a pair of medium-wash low-rise bootcut jeans and chunky platform sneakers for a classic, nostalgic look straight out of the early 2000s. Alternatively, tuck the top into a pleated tennis skirt paired with white ankle socks and retro trainers for a sweet, sporty outfit that balances casual and cute.

Model unavailable (one character of the key changed, then restored): The model couldn't be reached, so this step stopped. The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Then run this query again.

**On the MCP move:** `search_listings` is the only tool registered on the FitFindr MCP server. `run_agent` calls it through `call_tool` instead of importing it. The same query still returns the Y2K baby tee first, and an impossible query still returns an empty list and stops. The other tools stay direct function calls.



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
