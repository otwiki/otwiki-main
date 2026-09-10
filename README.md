# Optimal Transport Wiki

The [Optimal Transport Wiki](https://www.otwiki.xyz) is built with [Quarto](https://quarto.org).

Each article is a `.qmd` file in this repository. For example, `Monge.qmd` produces the [Monge Problem page](https://www.otwiki.xyz/Monge.html). The homepage is `index.qmd`.

To suggest an edit, open the article's `.qmd` file on GitHub, select the pencil icon, and propose the change in a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md) for syntax examples and preview instructions. To report a broken page, formula, citation, or link, [open an issue](https://github.com/otwiki/otwiki-main/issues/new/choose).

The `main` branch contains editable source files. After a pull request passes **Check wiki** and is merged, GitHub Actions renders and checks all pages, publishes the website, and updates `gh-pages` with the generated files. Do not edit `gh-pages` or commit `_site`.

The build uses Quarto **1.10.18**. The custom domain is recorded in `CNAME` and `_quarto.yml`. A failed check prevents publication; its details appear in the pull request's **Checks** tab or the repository's **Actions** tab.
