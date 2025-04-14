import marimo

__generated_with = "0.11.26"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# RSG Logs Visualization""")
    return


@app.cell
def _(mo, os):
    if not os.path.exists("logs"):
        os.mkdir("logs")

    file_browser = mo.ui.file_browser(
        initial_path="logs/",
        filetypes=[".csv"],
        multiple=False,
        restrict_navigation=True,
        label="CSV log file browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd):
    data = pd.read_csv(file_browser.path(0)) if len(file_browser.value) else None
    return (data,)


@app.cell
def _(data, file_browser, mo):
    mo.ui.table(
        data, label=f"Table from {file_browser.name(0)}"
    ) if data is not None else None
    return


@app.cell
def _(alt, data, mo):
    mo.ui.altair_chart(
        alt.Chart(data)
        .mark_line(interpolate="basis")  # also try 'step'.
        .encode(x=data.columns[0], y=data.columns[1]),
        label=f"Chart for {data.columns[0]} vs. {data.columns[1]}",
    ) if data is not None else None
    return


@app.cell(hide_code=True)
def _():
    import os
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, os, pd


if __name__ == "__main__":
    app.run()
