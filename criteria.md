# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:** Search scores keyword overlap, so a phrasing a person would still call a match ("old band shirt" for the bootleg graphic tee) can score zero and the loop stops with no fit card. The next two tools also call the model, and one try in five can come back blank. Five of five would require every phrasing to hit and both model calls to succeed every time.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:** This path only checks whether the search list is empty, then returns. It never calls the model, so temperature and wording cannot change the result. If the list is empty, the stop either happens or it does not. Four of five would let a loop that sometimes still calls `suggest_outfit` pass.

---

## 3. The item that was selected is the item the next tools received

In 5 of 5 runs where `search_results` is non-empty, `session["selected_item"]["id"]` equals `search_results[0]["id"]`, equals the `id` of the `new_item` argument passed to `suggest_outfit`, and equals the `id` of the `new_item` argument passed to `create_fit_card`.

**Why this target:** The check is string equality on an id. The model never gets a vote, so one mismatch means the session was overwritten or the wrong dict was passed. Four of five would treat that bug as noise.

---

## 4. Fit cards keep the facts and do not share an opening

For 5 different listings, with the response cache off, all 5 fit cards contain that listing's whole-dollar price (the digits before the decimal point) and its `platform` string, and at least 4 of the 5 cards have a first sentence (the text before the first period) that none of the other four share.

**Why this target:** Price and platform are copied from the listing, so a caption that omits them is a miss on all 5, not a style difference. The opening sentence is the part the model is free to vary, and at temperature 0.9 two captions can still start the same way. Requiring all 5 openings to differ would fail a run that did the job.

---

## 5. A price ceiling is never broken

For 5 queries that contain the words `under $30` and that each match at least one listing priced at or below 30, `search_results` is non-empty and every listing in it has `price` <= 30, in 5 of 5 tries.

**Why this target:** The check is a numeric comparison, same as criterion 2, so a single listing over $30 means the filter did not run. Four of five would excuse that. A tighter cap such as $15 would fail on queries whose only keyword hits cost more than $15, which is a ranking miss rather than a ceiling miss. The result list has to be non-empty so an empty list cannot pass by having nothing over the cap.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
