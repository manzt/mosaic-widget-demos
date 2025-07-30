# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "duckdb==1.2.2",
#     "marimo",
#     "matplotlib==3.10.3",
#     "mosaic-widget==0.18.0",
#     "numpy==2.3.2",
#     "polars==1.31.0",
#     "sqlglot==27.4.1",
# ]
# ///

import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium", sql_output="native")


@app.cell
def _():
    import marimo as mo
    import duckdb

    con = duckdb.connect()
    return con, mo


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE TABLE IF NOT EXISTS gaia AS -- compute u and v with natural earth projection
        WITH prep AS (
          SELECT
            radians((-l + 540) % 360 - 180) AS lambda,
            radians(b) AS phi,
            asin(sqrt(3)/2 * sin(phi)) AS t,
            t^2 AS t2,
            t2^3 AS t6,
            *
          FROM 'https://pub-1da360b43ceb401c809f68ca37c7f8a4.r2.dev/data/gaia-5m.parquet'
          WHERE parallax BETWEEN -5 AND 20 AND phot_g_mean_mag IS NOT NULL AND bp_rp IS NOT NULL
        )
        SELECT
          (1.340264 * lambda * cos(t)) / (sqrt(3)/2 * (1.340264 + (-0.081106 * 3 * t2) + (t6 * (0.000893 * 7 + 0.003796 * 9 * t2)))) AS u,
          t * (1.340264 + (-0.081106 * t2) + (t6 * (0.000893 + 0.003796 * t2))) AS v,
          * EXCLUDE('t', 't2', 't6')
        FROM prep
        """,
        engine=con,
    )
    return


@app.cell
def _(con, mo, spec):
    from mosaic_widget import MosaicWidget

    w = mo.ui.anywidget(MosaicWidget(spec, con=con, preagg_schema="mosaic"))
    w
    return (w,)


@app.cell
def _(con, w):
    con.sql(f"""
    SELECT * from gaia WHERE {w.params.get("brush", {}).get("predicate", "").replace("),(", ") AND (")} LIMIT 10
    """)
    return


@app.cell(hide_code=True)
def _():
    spec = {
        "meta": {
            "title": "Gaia Star Catalog",
            "description": "A 5M row sample of the 1.8B element Gaia star catalog.\nA `raster` sky map reveals our Milky Way galaxy. Select high parallax stars in the histogram to reveal a\n[Hertzsprung-Russel diagram](https://en.wikipedia.org/wiki/Hertzsprung%E2%80%93Russell_diagram)\nin the plot of stellar color vs. magnitude on the right.\n\n_You may need to wait a few seconds for the dataset to load._\n",
        },
        "data": {
            "gaia": "-- compute u and v with natural earth projection\nWITH prep AS (\n  SELECT\n    radians((-l + 540) % 360 - 180) AS lambda,\n    radians(b) AS phi,\n    asin(sqrt(3)/2 * sin(phi)) AS t,\n    t^2 AS t2,\n    t2^3 AS t6,\n    *\n  FROM 'https://pub-1da360b43ceb401c809f68ca37c7f8a4.r2.dev/data/gaia-5m.parquet'\n  WHERE parallax BETWEEN -5 AND 20 AND phot_g_mean_mag IS NOT NULL AND bp_rp IS NOT NULL\n)\nSELECT\n  (1.340264 * lambda * cos(t)) / (sqrt(3)/2 * (1.340264 + (-0.081106 * 3 * t2) + (t6 * (0.000893 * 7 + 0.003796 * 9 * t2)))) AS u,\n  t * (1.340264 + (-0.081106 * t2) + (t6 * (0.000893 + 0.003796 * t2))) AS v,\n  * EXCLUDE('t', 't2', 't6')\nFROM prep\n"
        },
        "params": {
            "brush": {"select": "crossfilter"},
            "bandwidth": 0,
            "pixelSize": 2,
            "scaleType": "sqrt",
        },
        "hconcat": [
            {
                "vconcat": [
                    {
                        "plot": [
                            {
                                "mark": "raster",
                                "data": {"from": "gaia", "filterBy": "$brush"},
                                "x": "u",
                                "y": "v",
                                "fill": "density",
                                "bandwidth": "$bandwidth",
                                "pixelSize": "$pixelSize",
                            },
                            {
                                "select": "intervalXY",
                                "pixelSize": 2,
                                "as": "$brush",
                            },
                        ],
                        "xyDomain": "Fixed",
                        "colorScale": "$scaleType",
                        "colorScheme": "viridis",
                        "width": 440,
                        "height": 250,
                        "marginLeft": 25,
                        "marginTop": 20,
                        "marginRight": 1,
                    },
                    {
                        "hconcat": [
                            {
                                "plot": [
                                    {
                                        "mark": "rectY",
                                        "data": {
                                            "from": "gaia",
                                            "filterBy": "$brush",
                                        },
                                        "x": {"bin": "phot_g_mean_mag"},
                                        "y": {"count": None},
                                        "fill": "steelblue",
                                        "inset": 0.5,
                                    },
                                    {"select": "intervalX", "as": "$brush"},
                                ],
                                "xDomain": "Fixed",
                                "yScale": "$scaleType",
                                "yGrid": True,
                                "width": 220,
                                "height": 120,
                                "marginLeft": 65,
                            },
                            {
                                "plot": [
                                    {
                                        "mark": "rectY",
                                        "data": {
                                            "from": "gaia",
                                            "filterBy": "$brush",
                                        },
                                        "x": {"bin": "parallax"},
                                        "y": {"count": None},
                                        "fill": "steelblue",
                                        "inset": 0.5,
                                    },
                                    {"select": "intervalX", "as": "$brush"},
                                ],
                                "xDomain": "Fixed",
                                "yScale": "$scaleType",
                                "yGrid": True,
                                "width": 220,
                                "height": 120,
                                "marginLeft": 65,
                            },
                        ]
                    },
                ]
            },
            {"hspace": 10},
            {
                "plot": [
                    {
                        "mark": "raster",
                        "data": {"from": "gaia", "filterBy": "$brush"},
                        "x": "bp_rp",
                        "y": "phot_g_mean_mag",
                        "fill": "density",
                        "bandwidth": "$bandwidth",
                        "pixelSize": "$pixelSize",
                    },
                    {"select": "intervalXY", "pixelSize": 2, "as": "$brush"},
                ],
                "xyDomain": "Fixed",
                "colorScale": "$scaleType",
                "colorScheme": "viridis",
                "yReverse": True,
                "width": 230,
                "height": 370,
                "marginLeft": 25,
                "marginTop": 20,
                "marginRight": 1,
            },
        ],
    }
    return (spec,)


if __name__ == "__main__":
    app.run()
