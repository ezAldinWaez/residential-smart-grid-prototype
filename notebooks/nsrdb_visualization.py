import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# NSRDB Visualization""")
    return


@app.cell
def _(Path, mo):
    _NSRDB_DIR = Path(__file__).parent.parent / "docs" / "_static" / "data" / "nsrdb"
    _NSRDB_DIR.mkdir(parents=True, exist_ok=True)

    file_browser = mo.ui.file_browser(
        initial_path=_NSRDB_DIR,
        filetypes=[".csv"],
        multiple=False,
        restrict_navigation=True,
        label="## NSRDB CSV File Browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd, timedelta, timezone):
    meta = (
        pd.read_csv(file_browser.path(0), nrows=1)
        if len(file_browser.value)
        else None
    )

    data = (
        pd.read_csv(file_browser.path(0), header=2)
        if len(file_browser.value)
        else None
    )

    if meta is not None and data is not None:
        tz_offset = int(meta["Local Time Zone"][0] - meta["Time Zone"][0])
        tz = timezone(timedelta(hours=tz_offset))

        data.insert(
            loc=0,
            column="Timestamp",
            value=pd.to_datetime(
                {
                    "year": data["Year"],
                    "month": data["Month"],
                    "day": data["Day"],
                    "hour": data["Hour"],
                    "minute": data["Minute"],
                },
                utc=True,
            ).dt.tz_convert(tz),
        )
        data.drop(columns=["Year", "Month", "Day",
                  "Hour", "Minute"], inplace=True)
        data.insert(
            loc=1,
            column="Time of Day",
            value=[
                "Day" if val < 90 else "Night"
                for val in data["Solar Zenith Angle"]
            ],
        )
    return data, meta


@app.cell
def _(meta, mo):
    mo.ui.table(meta, label=f"## NSRDB Metadata") if meta is not None else None
    return


@app.cell
def _(data, mo):
    mo.ui.table(data, label=f"## NSRDB Data") if data is not None else None
    return


@app.cell
def _(data, mo):
    field_options = (
        [col for col in data.columns if col not in ["Time of Day", "Timestamp"]]
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
        _time_start = data["Timestamp"].min()
        _time_end = _time_start + pd.Timedelta(weeks=1)

        _main_chart = (
            alt.Chart(data)
            .mark_line(interpolate="basis")  # also try 'step'.
            .encode(
                x=alt.X(
                    "Timestamp:T",
                    scale=alt.Scale(
                        domain=[_time_start, _time_end],
                        type="utc",
                    ),
                    axis=alt.Axis(format="%H:%M"),
                    title="Time",
                ),
                y=alt.Y(f"{field_selector.value}:Q",
                        title=field_selector.value),
                tooltip=["Timestamp:T", field_selector.value],
            )
            .properties(
                width=850, height=400, title=f"{field_selector.value} over Time"
            )
        )

        _timeline_df = data[["Timestamp", "Time of Day"]].copy()
        _timeline_df["y"] = 0

        _mode_timeline = (
            alt.Chart(_timeline_df)
            .mark_rule()
            .encode(
                x=alt.X(
                    "Timestamp:T",
                    scale=alt.Scale(
                        domain=[_time_start, _time_end],
                        type="utc",
                    ),
                    axis=alt.Axis(format="%y-%m-%d"),
                ),
                color=alt.Color(
                    "Time of Day:N",
                    scale=alt.Scale(domain=["Night", "Day"]),
                    legend=alt.Legend(title="Time of Day"),
                ),
                tooltip=["Timestamp:T", "Time of Day:N"],
            )
            .properties(width=850, height=50)
            .interactive()
        )

        chart = alt.vconcat(
            _main_chart, _mode_timeline).resolve_scale(x="shared")

    mo.vstack(
        [mo.md("## NSRDB Chart"), field_selector, chart]
    ) if data is not None else None
    return


@app.cell(hide_code=True)
def _():
    from datetime import datetime, timedelta, timezone
    import marimo as mo
    import pandas as pd
    import altair as alt
    from pathlib import Path
    return Path, alt, mo, pd, timedelta, timezone


if __name__ == "__main__":
    app.run()
