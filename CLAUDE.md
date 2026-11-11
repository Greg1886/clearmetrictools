# ClearMetricTools

Static website of personal-finance and tax calculators, published at clearmetrictools.com.
Every calculation runs in the visitor's browser. There is no backend, no build step, no
dependencies, no API keys and no network calls.

## Layout

| File | Tool | Audience |
|---|---|---|
| `index.html` | Broker FX, ETF TER and order-fee drag | Europe (EUR) |
| `pea-vs-cto.html` | PEA vs CTO tax comparison | France |
| `dividend-tax-leakage.html` | Accumulating vs distributing ETF tax leakage | Europe, by country |
| `crypto-tax-calculator.html` | Crypto net cash-out after tax | Multi-country |
| `75-15-10-planner.html` | 75/15/10 paycheck and FIRE planner | Any currency |
| `us/state-tax-migration.html` | State tax migration and capital gains | US |
| `us/roth-vs-traditional.html` | Roth vs Traditional IRA | US |
| `us/401k-penalty-calculator.html` | 401(k) early-withdrawal penalty | US |
| `about.html` | About & contact (text page, no calculator) | All, 4 languages |
| `privacy.html` | Privacy policy (text page, no calculator) | All, 4 languages |
| `robots.txt`, `sitemap.xml` | Search engine files. Add every new page to the sitemap. | |
| `CNAME` | Custom domain for hosting. Do not edit or delete. | |

## How a page is built

Each page is one self-contained `.html` file: its own `<style>`, markup and `<script>`.
Nothing is shared between files, so these blocks are copied into every page and must be
kept identical by hand:

- **Header and nav.** The five global pages link to each other and to `us/`. The three US
  pages have their own nav and link back with `../index.html`. Adding, renaming or
  removing a page means updating the nav in every file.
- **Theme.** CSS variables in `:root` (`--bg`, `--card`, `--accent`, ...) and the classes
  `.card`, `.input-group`, `.input-header`, `.input-val`, `.comparison-table`,
  `.loss-banner`. The export code finds inputs and results through these class names, so
  renaming one silently empties the export.
- **Translations.** The five global pages hold an `i18n` object with `en`, `fr`, `de`,
  `es`, applied by `applyLang()`. The choice is stored in `localStorage` as `cmt_lang`.
  The US pages are English only.
- **Disclaimer footer** (`#tDisclaimer`), in the same four languages on global pages.
- **Feedback button** linking to the Google Form, and the **export** functions
  `getSummaryText()`, `exportToTxt()`, `exportToPdf()` (PDF is the browser print dialog).
  The two text pages (`about.html`, `privacy.html`) have no calculator or export code.
- **Footer links** (`.legal-links`) to About and Privacy, placed above the disclaimer.
  On global pages the link text is in `i18n` (`linkAbout`, `linkPrivacy`).
- **Privacy policy facts.** `privacy.html` states that the site sets no cookies, has no
  analytics or ads, loads nothing from other domains and stores only `cmt_lang`. Any
  change to that (ads, analytics, a new stored value) must update the policy first.

Inputs are range sliders wired with `oninput="calc()"`. `calc()` reads every input,
recomputes, and writes the results into the page.

## Rules

### Always

- Change a shared block in all pages that contain it, then search the repo to confirm no
  copy was missed.
- Add every new visible string on a global page to all four languages in `i18n`.
- Keep the disclaimer footer on every page.
- Keep tax rates, thresholds and brackets as named values next to the formula that uses
  them, with a comment naming the tax year and the official source.
- Use relative links, and `../` from inside `us/`.

### Ask first

- Adding any external script, font, analytics, ad code or library. The site currently
  loads nothing from other domains.
- Adding a build step, a framework, or splitting CSS/JS into shared files.
- Renaming or moving a page (it breaks existing links and search results).
- Changing the wording of the disclaimer.
- Pushing to `main`. Treat it as publishing to the live site.

### Never

- Never invent or guess a tax rate, threshold, bracket or formula. If the rule is not
  confirmed by an official source for the stated tax year, stop and ask.
- Never change a number or formula as a side effect of a styling or layout change.
- Never send what a visitor types to any server.
- Never present a result as financial, tax or legal advice.

## Verification

There are no automated tests. Before calling a change done:

1. Open the changed page in a browser and check the console shows no errors.
2. For any change to a number or formula, work one example by hand (or from the official
   source's own example) and confirm the page shows the same result. Give the inputs, the
   expected value and the displayed value in the report.
3. Move each slider to its minimum and maximum and check for `NaN`, negative money or a
   broken layout.
4. On global pages, switch through all four languages and check no label stays in the
   previous language.
5. Test the TXT export and the print view.
6. Check the page at phone width (the grid collapses at 880px).

State plainly what was checked and what was not.
