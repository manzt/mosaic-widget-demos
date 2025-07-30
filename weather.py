# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "mosaic-widget==0.18.0",
#     "sqlglot==27.5.1",
# ]
# ///

import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo, w):
    _weather = w.params["click"].get("value")
    _range = w.params["range"].get("value")

    if _range:
        start = _range[0].split("T")[0]
        end = _range[1].split("T")[0]
    else:
        start = None
        end = None

    if _weather:
        _weather = [w[0] for w in _weather]

    mo.vstack(
        [
            mo.md(f"**Click selection**: `{_weather}`"),
            mo.md(f"**Range selection**: `{start=}, {end=}`"),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    import duckdb

    con = duckdb.connect()
    return (con,)


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE weather AS SELECT * FROM "https://uwdata.github.io/mosaic-datasets/data/seattle-weather.csv"
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(con, mo, spec):
    from mosaic_widget import MosaicWidget

    w = mo.ui.anywidget(MosaicWidget(spec, con=con, preagg_schema="mosaic"))
    w
    return (w,)


@app.cell
def _(con, mo, where):
    _df = mo.sql(
        f"""
        SELECT * FROM weather {where}
        """,
        engine=con
    )
    return


@app.cell
def _(w):
    predicates = " AND ".join([
        pred for pred in
        [
            w.params.get("range").get("predicate"),
            w.params.get("click").get("predicate"),
        ]
        if pred
    ])
    where = f"WHERE {predicates}" if predicates else ""
    return (where,)


@app.cell(hide_code=True)
def _():
    spec = {
        "meta": {
            "title": "Seattle Weather",
            "description": "An interactive view of Seattle's weather, including maximum temperature, amount of precipitation, and type of weather. By dragging on the scatter plot, you can see the proportion of days in that range that have sun, fog, drizzle, rain, or snow.\n",
            "credit": "Based on a [Vega-Lite/Altair example](https://vega.github.io/vega-lite/examples/interactive_seattle_weather.html) by Jake Vanderplas.",
        },
        "params": {
            "click": {"select": "single"},
            "domain": ["sun", "fog", "drizzle", "rain", "snow"],
            "colors": ["#e7ba52", "#a7a7a7", "#aec7e8", "#1f77b4", "#9467bd"],
        },
        "vconcat": [
            {
                "hconcat": [
                    {
                        "plot": [
                            {
                                "mark": "dot",
                                "data": {"from": "weather", "filterBy": "$click"},
                                "x": {"dateMonthDay": "date"},
                                "y": "temp_max",
                                "fill": "weather",
                                "r": "precipitation",
                                "fillOpacity": 0.7,
                            },
                            {
                                "select": "intervalX",
                                "as": "$range",
                                "brush": {"fill": "none", "stroke": "#888"},
                            },
                            {
                                "select": "highlight",
                                "by": "$range",
                                "fill": "#ccc",
                                "fillOpacity": 0.2,
                            },
                            {"legend": "color", "as": "$click", "columns": 1},
                        ],
                        "xyDomain": "Fixed",
                        "xTickFormat": "%b",
                        "colorDomain": "$domain",
                        "colorRange": "$colors",
                        "rDomain": "Fixed",
                        "rRange": [2, 10],
                        "width": 680,
                        "height": 300,
                    }
                ]
            },
            {
                "plot": [
                    {
                        "mark": "barX",
                        "data": {"from": "weather"},
                        "x": {"count": None},
                        "y": "weather",
                        "fill": "#ccc",
                        "fillOpacity": 0.2,
                    },
                    {
                        "mark": "barX",
                        "data": {"from": "weather", "filterBy": "$range"},
                        "x": {"count": None},
                        "y": "weather",
                        "fill": "weather",
                    },
                    {"select": "toggleY", "as": "$click"},
                    {"select": "highlight", "by": "$click"},
                ],
                "xDomain": "Fixed",
                "yDomain": "$domain",
                "yLabel": None,
                "colorDomain": "$domain",
                "colorRange": "$colors",
            },
        ],
    }
    return (spec,)


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
