---
name: manage-site
description: Workflows for changing, checking and publishing the ClearMetricTools website (clearmetrictools.com). Use this whenever the user asks to add or edit a calculator page, change the nav, header, footer, disclaimer, translations or styling, update a tax rate, threshold or formula, check the site for problems, or publish, deploy, push or "put live" any change, even if they only say "update the website" or "is the site OK?".
---

# Managing the ClearMetricTools site

Read `CLAUDE.md` in the repo root first. It holds the page list, the rules
(Always / Ask first / Never) and the manual verification steps. This skill adds
the step-by-step workflows and a checker script. If the two ever disagree,
`CLAUDE.md` wins and this file should be corrected.

## Why the site needs care

Each page is one self-contained HTML file. The nav, theme, translations,
disclaimer, feedback button and export code are copied into every page, so a
change made in one file and forgotten in another is the most common way this
site breaks. The second risk is a wrong tax number: a calculator that looks
fine but shows a wrong result is worse than one that is visibly broken.

## The checker

```bash
python .claude/skills/manage-site/scripts/check_site.py .
```

Run it before starting (to know the baseline) and after every change. It
reports, per page: broken local links, anything loaded from another domain,
a missing disclaimer, feedback link or export function, script references to
ids that no element has, duplicate ids, translation keys missing from any of
the four languages, and nav that differs between pages in the same folder.

It cannot tell whether a tax rate or formula is right. A clean run means the
plumbing is intact, nothing more. Say so when reporting.

## Workflows

### Change something shared (nav, theme, disclaimer, export code)

1. Search every `.html` file for the block, so you know how many copies exist.
   The five global pages and the three `us/` pages have different navs.
2. Make the same change in every copy.
3. Run the checker.
4. Open at least one global page and one `us/` page in the browser.

### Add a calculator page

1. Ask what the tool computes, for which country and tax year, and which
   official source defines the rules. Do not start from guessed rates.
2. Copy the most similar existing page as the starting point, so the shared
   blocks come along intact. Global pages go in the root, US pages in `us/`.
3. Replace the inputs, `calc()` and result markup. Keep the class names the
   export code relies on (`.input-group`, `.input-header`, `.comparison-table`,
   `.loss-banner`).
4. Global page: add every visible string to all four languages in `i18n`.
5. Add the page to the nav of every page in the same group.
6. Run the checker, then do the manual verification from `CLAUDE.md`.

### Change a tax rate, threshold or formula

1. Get the official source and tax year from the user, or find the official
   page and show it to them. If it cannot be confirmed, stop and ask.
2. Change only that value. Keep it as a named value with a comment giving the
   year and source.
3. Work one example by hand and confirm the page shows the same number. Report
   the inputs, the expected value and the displayed value.
4. Search the other pages for the same figure; the same rate may be repeated.

### Publish

The site is served by GitHub Pages from the `main` branch of
`Greg1886/clearmetrictools`, so a push to `main` is a release.

1. Run the checker. Do not publish with failures unless the user accepts them.
2. Work on a branch, commit there, and show the user what changed.
3. Push to `main` only after the user says to. Earlier approval for a
   different change does not carry over.
4. After pushing, wait a minute or two and confirm the live copy matches:

```bash
python .claude/skills/manage-site/scripts/check_site.py --live https://clearmetrictools.com .
```

   "Live copy differs" right after a push usually means Pages is still
   building; check again before treating it as a failure.

Everything in the repo root is public once pushed, including `CLAUDE.md`.
Never put anything private in this repository.

## Reporting

End with what changed, what the checker said, what was verified by hand, and
what was not verified.
