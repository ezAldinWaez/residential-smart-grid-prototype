import marimo

__generated_with = "0.10.17"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"# Edit Graph")
    return


@app.cell
def _(mo):
    file_browser = mo.ui.file_browser(
        initial_path="graphs/",
        filetypes=['.mermaid'],
        multiple=False,
        restrict_navigation=True,
        label="Mermaid graph file browser"
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, mo):
    def _get_code_editor_value():
        if len(file_browser.value):
            with open(file_browser.path(0), 'r') as _mermaid_file:
                value = _mermaid_file.read()
                _mermaid_file.close()
        else:
            value = ""
        return value

    graph_code_editor = mo.ui.code_editor(
        value=_get_code_editor_value(),
        label="Graph Code Editor",
        language="mermaid",
    )
    return (graph_code_editor,)


@app.cell
def _(graph_code_editor, mo):
    graph_rendering = mo.md(f"""
        Graph Rendering
        {mo.mermaid(graph_code_editor.value)}
    """)
    return (graph_rendering,)


@app.cell
def _(graph_code_editor, graph_rendering, mo):
    mo.ui.tabs({
        "Graph Code Editor": graph_code_editor,
        "Graph Rendering": graph_rendering,
    })
    return


@app.cell
def _(file_browser, graph_code_editor, mo):
    def update_file(v):
        try:
            if len(file_browser.value):
                with open(file_browser.path(0), 'w') as _mermaid_file:
                    _mermaid_file.write(graph_code_editor.value)
                    _mermaid_file.close()
                return "Graph file have been saved successfully."
            else:
                return "There is no graph file selected!"
        except Exception as e:
            print(e)
            return "Could not save the graph file!"

    update_button = mo.ui.button(on_click=update_file, value="", label="Update Graph File")
    return update_button, update_file


@app.cell
def _(mo, update_button):
    mo.hstack([
        update_button,
        update_button.value
    ], justify="start", align="center", gap=1)
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
