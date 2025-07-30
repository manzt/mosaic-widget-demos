# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "mosaic-widget==0.18.0",
#     "polars==1.31.0",
# ]
# ///

import marimo

__generated_with = "0.14.12"
app = marimo.App(width="medium")


@app.cell
def _(spec):
    import marimo as mo
    import polars as pl
    from mosaic_widget import MosaicWidget

    proteins = pl.read_parquet(
        "https://github.com/uwdata/mosaic/raw/refs/heads/main/data/protein-design.parquet"
    )

    mo.ui.anywidget(
        MosaicWidget(spec, data={"proteins": proteins}, preagg_schema="mosaic")
    )
    return


@app.cell(hide_code=True)
def _():
    spec = {
        "meta": {
            "title": "Protein Design Explorer",
            "description": 'Explore synthesized proteins generated via\n[RFDiffusion](https://www.bakerlab.org/2023/07/11/diffusion-model-for-protein-design/).\n"Minibinders" are small proteins that bind to a specific protein target.\nWhen designing a minibinder, a researcher inputs the structure of the\ntarget protein and other parameters into the AI diffusion model. Often, a\nsingle, promising (parent) _version_ can be run through the model again to\nproduce additional, similar designs to better sample the design space.\n\nThe pipeline generates tens of thousands of protein designs. The metric\n_pAE_ (predicted alignment error) measures how accurate a model was at\npredicting the minibinder shape, whereas _pLDDT_ (predicted local distance\ndifference test) measures a model\'s confidence in minibinder structure\nprediction. For _pAE_ lower is better, for _pLDDT_ higher is better.\n\nAdditional parameters include _partial t_ to set the time steps used by\nthe model, _noise_ to create more diversity of designs, _gradient decay\nfunction_ and _gradient scale_ to guide prioritizing different positions\nat different time points, and _movement_ to denote whether the minibinder\nwas left in its original position ("og") or moved to a desirable position\n("moved").\n\nThe dashboard below enables exploration of the results to identify\npromising protein designs and assess the effects of process parameters.\n',
            "credit": "Adapted from a [UW CSE 512](https://courses.cs.washington.edu/courses/cse512/24sp/) project by Christina Savvides, Alexander Shida, Riti Biswas, and Nora McNamara-Bordewick. Data from the [UW Institute for Protein Design](https://www.ipd.uw.edu/).\n",
        },
        "params": {
            "query": {"select": "crossfilter"},
            "point": {"select": "intersect", "empty": True},
            "plddt_domain": [67, 94.5],
            "pae_domain": [5, 29],
            "scheme": "observable10",
        },
        "vconcat": [
            {
                "hconcat": [
                    {
                        "input": "menu",
                        "from": "proteins",
                        "column": "partial_t",
                        "label": "Partial t",
                        "as": "$query",
                    },
                    {
                        "input": "menu",
                        "from": "proteins",
                        "column": "noise",
                        "label": "Noise",
                        "as": "$query",
                    },
                    {
                        "input": "menu",
                        "from": "proteins",
                        "column": "gradient_decay_function",
                        "label": "Gradient Decay",
                        "as": "$query",
                    },
                    {
                        "input": "menu",
                        "from": "proteins",
                        "column": "gradient_scale",
                        "label": "Gradient Scale",
                        "as": "$query",
                    },
                ]
            },
            {"vspace": "1.5em"},
            {
                "hconcat": [
                    {
                        "plot": [
                            {
                                "mark": "rectY",
                                "data": {"from": "proteins", "filterBy": "$query"},
                                "x": {"bin": "plddt_total", "steps": 60},
                                "y": {"count": None},
                                "z": "version",
                                "fill": "version",
                                "order": "z",
                                "reverse": True,
                                "insetLeft": 0.5,
                                "insetRight": 0.5,
                            }
                        ],
                        "width": 600,
                        "height": 55,
                        "xAxis": None,
                        "yAxis": None,
                        "xDomain": "$plddt_domain",
                        "colorDomain": "Fixed",
                        "colorScheme": "$scheme",
                        "marginLeft": 40,
                        "marginRight": 0,
                        "marginTop": 0,
                        "marginBottom": 0,
                    },
                    {"hspace": 5},
                    {
                        "legend": "color",
                        "for": "scatter",
                        "columns": 1,
                        "as": "$query",
                    },
                ]
            },
            {
                "hconcat": [
                    {
                        "name": "scatter",
                        "plot": [
                            {"mark": "frame", "stroke": "#ccc"},
                            {
                                "mark": "raster",
                                "data": {"from": "proteins", "filterBy": "$query"},
                                "x": "plddt_total",
                                "y": "pae_interaction",
                                "fill": "version",
                                "pad": 0,
                            },
                            {
                                "select": "intervalXY",
                                "as": "$query",
                                "brush": {
                                    "stroke": "currentColor",
                                    "fill": "transparent",
                                },
                            },
                            {
                                "mark": "dot",
                                "data": {"from": "proteins", "filterBy": "$point"},
                                "x": "plddt_total",
                                "y": "pae_interaction",
                                "fill": "version",
                                "stroke": "currentColor",
                                "strokeWidth": 0.5,
                            },
                        ],
                        "opacityDomain": [0, 2],
                        "opacityClamp": True,
                        "colorDomain": "Fixed",
                        "colorScheme": "$scheme",
                        "xDomain": "$plddt_domain",
                        "yDomain": "$pae_domain",
                        "xLabelAnchor": "center",
                        "yLabelAnchor": "center",
                        "marginTop": 0,
                        "marginLeft": 40,
                        "marginRight": 0,
                        "width": 600,
                        "height": 450,
                    },
                    {
                        "plot": [
                            {
                                "mark": "rectX",
                                "data": {"from": "proteins", "filterBy": "$query"},
                                "x": {"count": None},
                                "y": {"bin": "pae_interaction", "steps": 60},
                                "z": "version",
                                "fill": "version",
                                "order": "z",
                                "reverse": True,
                                "insetTop": 0.5,
                                "insetBottom": 0.5,
                            }
                        ],
                        "width": 55,
                        "height": 450,
                        "xAxis": None,
                        "yAxis": None,
                        "marginTop": 0,
                        "marginLeft": 0,
                        "marginRight": 0,
                        "yDomain": "$pae_domain",
                        "colorDomain": "Fixed",
                        "colorScheme": "$scheme",
                    },
                ]
            },
            {"vspace": "1em"},
            {
                "input": "table",
                "as": "$point",
                "filterBy": "$query",
                "from": "proteins",
                "columns": [
                    "version",
                    "pae_interaction",
                    "plddt_total",
                    "noise",
                    "gradient_decay_function",
                    "gradient_scale",
                    "movement",
                ],
                "width": 680,
                "height": 215,
            },
        ],
    }
    return (spec,)


if __name__ == "__main__":
    app.run()
