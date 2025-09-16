import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""# Virtual Battery Logs Visualization""")
    return


@app.cell
def _(mo):
    refresh = mo.ui.refresh(default_interval="1s")
    refresh
    return (refresh,)


@app.cell
def _(Path, mo):
    _RSGP_LOGS_DIR = Path(__file__).parent.parent / "rsgp" / "_logs"
    _RSGP_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    file_browser = mo.ui.file_browser(
        initial_path=_RSGP_LOGS_DIR,
        filetypes=[".csv"],
        multiple=False,
        restrict_navigation=True,
        label="Power management CSV log file browser",
    )
    file_browser
    return (file_browser,)


@app.cell
def _(file_browser, pd, refresh):
    refresh

    data = None
    if len(file_browser.value) and file_browser.name(0) == "power_management.csv":
        try:
            data = pd.read_csv(file_browser.path(0))
            if data is not None and not data.empty:
                data["timestamp"] = pd.to_datetime(data["timestamp"])

                # Filter last 24 hours
                latest_time = data["timestamp"].max()
                start_time = latest_time - pd.Timedelta(hours=24)
                data = data[data["timestamp"] >= start_time].copy()
        except Exception as e:
            data = None
    return (data,)


@app.cell
def _(alt, data, mo, refresh):
    refresh

    if data is None or data.empty:
        chart = mo.md("*No data available for visualization*")
    else:
        # Convert capacities from Wh to kWh - create stacked data for both total and residual
        chart_data = data.copy()
        # Total capacities
        chart_data["house_1_total_kwh"] = chart_data["virtual_battery_1_total_capacity"] / 1000
        chart_data["house_2_total_kwh"] = chart_data["virtual_battery_2_total_capacity"] / 1000  
        chart_data["house_3_total_kwh"] = chart_data["virtual_battery_3_total_capacity"] / 1000
        # Residual capacities
        chart_data["house_1_residual_kwh"] = chart_data["virtual_battery_1_residual_capacity"] / 1000
        chart_data["house_2_residual_kwh"] = chart_data["virtual_battery_2_residual_capacity"] / 1000
        chart_data["house_3_residual_kwh"] = chart_data["virtual_battery_3_residual_capacity"] / 1000

        # Create cumulative sums for stacked areas
        chart_data["house_1_total_cumsum"] = chart_data["house_1_total_kwh"]
        chart_data["house_2_total_cumsum"] = chart_data["house_1_total_kwh"] + chart_data["house_2_total_kwh"]
        chart_data["house_3_total_cumsum"] = chart_data["house_1_total_kwh"] + chart_data["house_2_total_kwh"] + chart_data["house_3_total_kwh"]

        # Residual capacity positions (at bottom of each house's total capacity)
        chart_data["house_1_residual_start"] = 0
        chart_data["house_1_residual_end"] = chart_data["house_1_residual_kwh"]
        chart_data["house_2_residual_start"] = chart_data["house_1_total_kwh"] 
        chart_data["house_2_residual_end"] = chart_data["house_1_total_kwh"] + chart_data["house_2_residual_kwh"]
        chart_data["house_3_residual_start"] = chart_data["house_1_total_kwh"] + chart_data["house_2_total_kwh"]
        chart_data["house_3_residual_end"] = chart_data["house_1_total_kwh"] + chart_data["house_2_total_kwh"] + chart_data["house_3_residual_kwh"]

        # Create base chart (non-interactive)
        base = alt.Chart(chart_data)

        # Total capacity areas (lower opacity)
        total_area1 = base.mark_area(
            opacity=0.6,
            color='red'
        ).encode(
            x=alt.X('timestamp:T', 
                   axis=alt.Axis(format='%H:%M'),
                   title='Time'),
            y=alt.Y('house_1_total_cumsum:Q',
                   title='Capacity [kWh]'),
            tooltip=['timestamp:T', alt.Tooltip('house_1_total_kwh:Q', title='House 1 Total [kWh]')]
        )

        total_area2 = base.mark_area(
            opacity=0.6,
            color='green'
        ).encode(
            x='timestamp:T',
            y='house_1_total_kwh:Q',
            y2='house_2_total_cumsum:Q',
            tooltip=['timestamp:T', alt.Tooltip('house_2_total_kwh:Q', title='House 2 Total [kWh]')]
        )

        total_area3 = base.mark_area(
            opacity=0.6,
            color='blue'
        ).encode(
            x='timestamp:T',
            y='house_2_total_cumsum:Q',
            y2='house_3_total_cumsum:Q',
            tooltip=['timestamp:T', alt.Tooltip('house_3_total_kwh:Q', title='House 3 Total [kWh]')]
        )

        # Residual capacity areas (higher opacity, positioned at bottom of each house's area)
        residual_area1 = base.mark_area(
            opacity=0.3,
            color='red'
        ).encode(
            x='timestamp:T',
            y='house_1_residual_start:Q',
            y2='house_1_residual_end:Q',
            tooltip=['timestamp:T', alt.Tooltip('house_1_residual_kwh:Q', title='House 1 Residual [kWh]')]
        )

        residual_area2 = base.mark_area(
            opacity=0.3,
            color='green'
        ).encode(
            x='timestamp:T',
            y='house_2_residual_start:Q',
            y2='house_2_residual_end:Q',
            tooltip=['timestamp:T', alt.Tooltip('house_2_residual_kwh:Q', title='House 2 Residual [kWh]')]
        )

        residual_area3 = base.mark_area(
            opacity=0.3,
            color='blue'
        ).encode(
            x='timestamp:T',
            y='house_3_residual_start:Q',
            y2='house_3_residual_end:Q',
            tooltip=['timestamp:T', alt.Tooltip('house_3_residual_kwh:Q', title='House 3 Residual [kWh]')]
        )

        # Layer all areas: total capacities first (background), then residual capacities (foreground)
        chart = alt.layer(
            total_area1, total_area2, total_area3,  # Total capacity (low opacity)
            residual_area1, residual_area2, residual_area3  # Residual capacity (high opacity)
        ).properties(
            width=850,
            height=400,
            title="Virtual Battery Total and Residual Capacity (Last 24 Hours)"
        )

    mo.vstack([
        mo.md("## Virtual Battery Charge Levels Chart"),
        chart
    ])
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
