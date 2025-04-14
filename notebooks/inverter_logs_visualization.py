import marimo

__generated_with = "0.11.26"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"# Inverter Logs Visualization")
    return


@app.cell
def _(mo, os):
    if not os.path.exists("data/"):
        os.mkdir("data/")

    if not os.path.exists('data/inverter_logs/'):
        os.mkdir("data/inverter_logs/")

    file_browser = mo.ui.file_browser(
        initial_path="data/inverter_logs/",
        filetypes=['.xls'],
        multiple=False,
        restrict_navigation=True,
        label="## Inverter Logs XLS File Browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd):
    # data = pd.read_excel("ftp://admin@192.168.1.2:2121/watchpower/DataLog_929321041053717.xls", engine='xlrd')
    data = pd.read_excel(file_browser.path(0), engine='xlrd') if len(file_browser.value) else None

    if data is not None:
        data["Time"] = pd.to_datetime(data["Time"])

    field_options = [col for col in data.columns if col not in ["Time", "Device mode"]] if data is not None else None
    return data, field_options


@app.cell
def _(data, field_options, mo):
    field_selector = mo.ui.dropdown(
        options=field_options,
        value=field_options[0],
        label="Select field to visualize: ",
    ) if data is not None else None
    return (field_selector,)


@app.cell
def _(alt, data, field_selector, mo, pd):
    if data is None:
        chart = None

    else:
        _time_start = pd.Timestamp(data["Time"].dt.date.iloc[0])
        _time_end = _time_start + pd.Timedelta(days=1)

        _main_chart = (
            alt.Chart(data)
            .mark_line(interpolate="basis")
            .encode(
                x=alt.X(
                    "Time:T",
                    scale=alt.Scale(domain=[_time_start, _time_end]),
                    axis=alt.Axis(format="%H:%M"),
                ),
                y=alt.Y(f"{field_selector.value}:Q"),
                tooltip=["Time", field_selector.value],
            )
            .properties(width=850, height=400, title=f"{field_selector.value} over Time")
        )

        _timeline_data = data[["Time", "Device mode"]].copy()
        _timeline_data["y"] = 0

        _mode_timeline = (
            alt.Chart(_timeline_data)
            .mark_rule()
            .encode(
                x=alt.X(
                    "Time:T",
                    scale=alt.Scale(domain=[_time_start, _time_end]),
                    axis=alt.Axis(format="%H:%M"),
                ),
                color="Device mode:N",
                tooltip=["Time", "Device mode"],
            )
            .properties(width=850, height=50)
            .interactive()
        )

        chart = alt.vconcat(_main_chart, _mode_timeline).resolve_scale(x="shared")


    mo.vstack([
        mo.md("## Inverter Logs Chart"),
        field_selector,
        chart
    ]) if data is not None else None
    return (chart,)


@app.cell(hide_code=True)
def _():
    import os
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, os, pd


if __name__ == "__main__":
    app.run()
