import marimo

__generated_with = "0.10.7"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"# Plot CSV Log")
    return


@app.cell
def _(mo):
    file_browser = mo.ui.file_browser(
        initial_path="logs/",
        filetypes=['.csv'],
        multiple=False,
        restrict_navigation=True,
        label="CSV log file browser"
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd):
    data = pd.read_csv(file_browser.path(0)) if len(file_browser.value) else None
    return (data,)


@app.cell
def _(data, file_browser, mo):
    mo.ui.table(data, label=f"Table from {file_browser.name(0)}") if data is not None else None
    return


@app.cell
def _(alt, data):
    chart = alt.Chart(data).mark_line().encode(
        x=data.columns[0],
        y=data.columns[1],
    ) if data is not None else None
    return (chart,)


@app.cell
def _(chart, data, mo):
    mo.ui.altair_chart(chart, label=f"Chart for {data.columns[0]} vs. {data.columns[1]}") if chart is not None else None
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, pd


if __name__ == "__main__":
    app.run()
