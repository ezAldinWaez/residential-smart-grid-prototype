import marimo

__generated_with = "0.10.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"# RSG System Graph")
    return


@app.cell
def _(code_editor, mo):
    mo.md(f"""{mo.mermaid(code_editor.value)}""")
    return


@app.cell
def _(mo):
    with open("rsg_system_graph.mermaid", 'r') as _mermaid_file:
        code_editor = mo.ui.code_editor(
            value=_mermaid_file.read(),
            language="mermaid",
            label="RSG system graph mermaid code editor",
        )
        _mermaid_file.close()

    code_editor
    return (code_editor,)


@app.cell
def _(code_editor, mo):
    def update_file(v):
        try:
            with open("rsg_system_graph.mermaid", 'w') as _mermaid_file:
                _mermaid_file.write(code_editor.value)
                _mermaid_file.close()
            return "Mermaid file have been saved successfully."
        except Exception as e:
            print(e)
            return "Could not save the mermaid file!"

    update_button = mo.ui.button(on_click=update_file, value="", label="Update Mermaid File")
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
