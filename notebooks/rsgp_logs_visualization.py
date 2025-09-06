import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# RSGP Logs Visualization""")
    return


@app.cell
def _(Path, mo):
    _RSGP_LOGS_DIR = Path(__file__).parent.parent / "rsgp" / "_logs"
    _RSGP_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    file_browser = mo.ui.file_browser(
        initial_path=_RSGP_LOGS_DIR,
        filetypes=[".csv"],
        multiple=False,
        restrict_navigation=True,
        label="CSV log file browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd):
    data = pd.read_csv(file_browser.path(0)) if len(
        file_browser.value) else None
    if data is not None:
        data["timestamp"] = pd.to_datetime(data["timestamp"], format='ISO8601')
    return (data,)


@app.cell
def _(data, file_browser, mo):
    mo.ui.table(
        data, label=f"Table from {file_browser.name(0)}"
    ) if data is not None else None
    return


@app.cell
def _(data, mo):
    field_options = (
        [col for col in data.columns if col not in ["timestamp"]]
        if data is not None
        else None
    )

    field_selector = (
        mo.ui.dropdown(
            options=field_options,
            value=field_options[0],
            label="Select field to visualize: ",
        )
        if field_options
        else None
    )
    return (field_selector,)


@app.cell
def _(alt, data, field_selector, mo, pd):
    if data is None:
        chart = None
    else:
        _time_start = data["timestamp"].min()
        _time_end = _time_start + pd.Timedelta(weeks=1)

        _main_chart = (
            alt.Chart(data)
            .mark_line(interpolate="basis")  # also try 'step'.
            .encode(
                x=alt.X(
                    "timestamp:T",
                    scale=alt.Scale(
                        domain=[_time_start, _time_end],
                        type="utc",
                    ),
                    axis=alt.Axis(format="%H:%M"),
                    title="Time",
                ),
                y=alt.Y(f"{field_selector.value}:Q",
                        title=field_selector.value),
                tooltip=["timestamp:T", field_selector.value],
            )
            .properties(
                width=850, height=400, title=f"{field_selector.value} over Time"
            )
        )

        _timeline_df = data[["timestamp"]].copy()
        _timeline_df["y"] = 0

        _mode_timeline = (
            alt.Chart(_timeline_df)
            .mark_rule()
            .encode(
                x=alt.X(
                    "timestamp:T",
                    scale=alt.Scale(
                        domain=[_time_start, _time_end],
                        type="utc",
                    ),
                    axis=alt.Axis(format="%y-%m-%d"),
                ),
                tooltip=["timestamp:T"],
            )
            .properties(width=850, height=50)
            .interactive()
        )

        chart = alt.vconcat(
            _main_chart, _mode_timeline).resolve_scale(x="shared")

    mo.vstack(
        [mo.md("## RSGP Logs Chart"), field_selector, chart]
    ) if data is not None else None
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    from pathlib import Path
    return Path, alt, mo, pd


if __name__ == "__main__":
    app.run()
