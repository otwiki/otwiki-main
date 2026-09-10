# Editing the wiki

## Propose an edit on GitHub

1. Find the page's `.qmd` file. The filename matches the page address: `Monge.html` comes from `Monge.qmd`.
2. Open that file on GitHub and select the pencil icon. GitHub may offer to create a fork if you do not have write access.
3. Edit the source. Choose **Commit changes**, select a new branch, and open a pull request describing the change.
4. Wait for **Check wiki** to pass. If it fails, open **Details** to see the filename and problem, then edit the same branch to correct it.
5. A maintainer can merge the pull request after checking the changes. The **Publish wiki** job then updates the live website automatically.

GitHub's file preview does not reproduce every Quarto feature. Use a local Quarto preview when you need to inspect the finished page.

## Preview on your computer

Install [Quarto 1.10.18](https://github.com/quarto-dev/quarto-cli/releases/tag/v1.10.18), download or clone this repository, and open a terminal in its folder. Preview a page with:

```sh
quarto preview Monge.qmd
```

For filenames containing spaces, put the filename in quotes. To build every page:

```sh
quarto render --fail-if-warnings
```

The generated website appears in `_site`. This folder is ignored by Git; edit the `.qmd` source files instead.

## Working syntax

Use ordinary Markdown for headings, emphasis, and lists:

```markdown
## Section heading

**Bold text** and *italic text*.

- First item
- Second item
```

Use dollar signs for formulas. Do not use the old wiki's `<math>` tags.

```markdown
Inline: $x^2$.

$$
f(x) = x^2
$$
```

Link to the source filename for another wiki page, and use a full URL for an external page:

```markdown
[Monge Problem](Monge.qmd)
[Quarto documentation](https://quarto.org/docs/authoring/markdown-basics.html)
```

For bibliography citations, select the appropriate existing `.bib` file in the page's opening metadata and use a key from that file:

```markdown
---
title: "Page title"
bibliography: CTMOT_bibliography.bib
---

An existing reference [@henrylabordere2017model].
```

The same source can be cited repeatedly with the same key. For reference text without a bibliography entry, use a Markdown footnote instead of `<ref>` tags:

```markdown
A sentence with a reference.[^reference-name]

[^reference-name]: Existing author, title, and publication information.
```

Close each Quarto proof or theorem block before beginning another section:

```markdown
::: {.proof}
Proof text.
:::
```

## Run the automatic checks locally

In addition to Quarto, install Node.js 24, Python 3, and pnpm 11.19.0. Then run:

```sh
pnpm install --frozen-lockfile
pnpm exec playwright install chromium
quarto render --fail-if-warnings
pnpm check
```

On Linux, use `pnpm exec playwright install --with-deps chromium` to install browser system dependencies too. The browser checks need internet access to load MathJax and externally hosted article images.

The checks cover all article pages, missing citations, internal links and anchors, missing local resources, obsolete wiki markup, nested proof blocks, formula rendering errors, and article images. They check rendering and syntax; they do not judge mathematical content or writing style.
