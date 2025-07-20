import marimo

__generated_with = "0.12.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# Graphs Editor""")
    return


@app.cell
def _(mo, os, Path):
    _GRAPHS_DIR = Path(__file__).parent.parent / "docs" / "_static" / "graphs"
    _GRAPHS_DIR.mkdir(parents=True, exist_ok=True)

    file_browser = mo.ui.file_browser(
        initial_path=_GRAPHS_DIR,
        filetypes=[".mermaid"],
        multiple=False,
        restrict_navigation=True,
        label="## Mermaid File Browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, mo):
    def _get_code_editor_value():
        if len(file_browser.value):
            with open(
                file_browser.path(0), encoding="utf-8", mode="r"
            ) as _mermaid_file:
                value = _mermaid_file.read()
                _mermaid_file.close()
        else:
            value = ""
        return value

    graph_code_editor = mo.ui.code_editor(
        value=_get_code_editor_value(),
        label="### Graph Code Editor",
        language="mermaid",
    )
    return (graph_code_editor,)


@app.cell
def _(graph_code_editor, mo):
    graph_rendering = mo.md(
        (f"### Graph Rendering\n{mo.mermaid(graph_code_editor.value)}\n")
    )
    return (graph_rendering,)


@app.cell
def _(file_browser, graph_code_editor, mo):
    def update_file(v):
        if not file_browser.value:
            return "There is no graph file selected!"

        try:
            with open(
                file_browser.path(0), encoding="utf-8", mode="w"
            ) as _mermaid_file:
                _mermaid_file.write(graph_code_editor.value)
                _mermaid_file.close()
            return "Graph file have been saved successfully."

        except Exception as e:
            print(e)
            return "Could not save the graph file!"

    update_button = mo.ui.button(
        on_click=update_file, value="", label="Update Graph File"
    )
    return update_button, update_file


@app.cell
def _(file_browser, graph_code_editor, graph_rendering, mo, update_button):
    mo.vstack(
        [
            mo.md("## Mermaid Graph"),
            mo.ui.tabs(
                {
                    "Graph Rendering": graph_rendering,
                    "Graph Code Editor": graph_code_editor,
                }
            ),
            mo.hstack(
                [update_button, update_button.value],
                justify="start",
                align="center",
                gap=1,
            ),
        ]
    ) if len(file_browser.value) else None
    return


@app.cell(hide_code=True)
def _():
    import os
    import marimo as mo
    from pathlib import Path
    return mo, os, Path


if __name__ == "__main__":
    app.run()
