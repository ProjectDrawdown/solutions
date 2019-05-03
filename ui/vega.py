"""Functions to support the Drawdown models in Jupyter notebooks."""

import pandas as pd

pd.set_option('display.max_columns', 200)
pd.set_option('display.max_rows', 200)

# stable colors to be applied to Drawdown solution sectors.
sector_colormap = {
    'Materials': 'RebeccaPurple',
    'Electricity Generation': 'Peru',
    'Food': 'FireBrick',
    'Land Use': 'Green',
    'Women and Girls': 'DarkGoldenRod',
    'Transport': 'Teal',
    'Buildings and Cities': 'SteelBlue',
    'Oceans': 'Aquamarine',
}

def get_sector_color(sector):
  """Convenience method with a default, intended for Pandas apply() operations."""
  return sector_colormap.get(sector, 'Beige')

def solution_treemap(solutions, width, height):
  """Return a Vega description of a treemap of sectors + solutions.
     Vega grammar: https://vega.github.io/vega/docs/

     Arguments:
       solutions: Pandas DataFrame with columns 'Solution', 'Sector', and 'CO2eq'
       width, height: in pixels
  """
  elements = {'root': {'id': 1}}
  elements['row1'] = {'id': 2, 'parent': 1}
  elements['row2'] = {'id': 3, 'parent': 1}
  elements['row3'] = {'id': 4, 'parent': 1}
  idx = 5
  for name in ['Transport', 'Oceans', 'Materials']:
    elements[name] = {'id': idx, 'name': name, 'parent': 2, 'color': get_sector_color(name)}
    idx += 1
  for name in ['Electricity Generation', 'Food']:
    elements[name] = {'id': idx, 'name': name, 'parent': 3, 'color': get_sector_color(name)}
    idx += 1
  for name in ['Land Use', 'Buildings and Cities', 'Women and Girls']:
    elements[name] = {'id': idx, 'name': name, 'parent': 4, 'color': get_sector_color(name)}
    idx += 1
  for row in solutions.itertuples(index=False):
    name = getattr(row, 'Solution')
    sector = getattr(row, 'Sector')
    co2eq = getattr(row, 'CO2eq')
    parent_id = elements.get(sector, 1)['id']
    elements[name] = {'id': idx, 'name': name, 'parent': parent_id, 'size': co2eq}
    idx += 1

  # Vega treemap documentation: https://vega.github.io/vega/examples/treemap/
  return {
      "$schema": "https://vega.github.io/schema/vega/v4.json",
      "width": width,
      "height": height,
      "padding": 2.5,
      "autosize": "none",

      "signals": [
        {
          "name": "layout", "value": "squarify",
        },
        {
          "name": "aspectRatio", "value": 1.4,
        }
      ],

      "data": [
        {
          "name": "drawdown",
          "values": list(elements.values()),
          "transform": [
            {
              "type": "stratify",
              "key": "id",
              "parentKey": "parent"
            },
            {
              "type": "treemap",
              "field": "size",
              "round": True,
              "method": {"signal": "layout"},
              "ratio": {"signal": "aspectRatio"},
              "size": [{"signal": "width"}, {"signal": "height"}]
            }
          ]
        },
        {
          "name": "nodes",
          "source": "drawdown",
          "transform": [{ "type": "filter", "expr": "datum.children" }]
        },
        {
          "name": "leaves",
          "source": "drawdown",
          "transform": [{ "type": "filter", "expr": "!datum.children" }]
        }
      ],

      "scales": [
        {
          "name": "color",
          "type": "ordinal",
          "domain": list(sector_colormap.keys()),
          "range": list(sector_colormap.values())
        },
      ],

      "marks": [
        {
          "type": "rect",
          "from": {"data": "nodes"},
          "interactive": False,
          "encode": {
            "enter": {
              "fill": {"scale": "color", "field": "name"}
            },
            "update": {
              "x": {"field": "x0"},
              "y": {"field": "y0"},
              "x2": {"field": "x1"},
              "y2": {"field": "y1"}
            }
          }
        },
        {
          "type": "rect",
          "from": {"data": "leaves"},
          "encode": {
            "enter": {
              "stroke": {"value": "#fff"},
              "tooltip": {"signal": "{title: datum.name, 'CO2eq': format(datum['size'], '.2f') + ' Gigatons'}"}
            },
            "update": {
              "x": {"field": "x0"},
              "y": {"field": "y0"},
              "x2": {"field": "x1"},
              "y2": {"field": "y1"},
              "fill": {"value": "transparent"}
            },
            "hover": {
              "fill": {"value": "gray"}
            }
          }
        },
        {
          "type": "text",
          "from": {"data": "nodes"},
          "interactive": False,
          "encode": {
            "enter": {
              "font": {"value": "Helvetica Neue, Arial"},
              "align": {"value": "center"},
              "baseline": {"value": "middle"},
              "fill": {"value": "#fff"},
              "text": {"field": "name"},
              "fontSize": {"value": 18},
              "fillOpacity": {"value": 1.0},
              "angle": {"value": -62.0}
            },
            "update": {
              "x": {"signal": "0.5 * (datum.x0 + datum.x1)"},
              "y": {"signal": "0.5 * (datum.y0 + datum.y1)"}
            }
          }
        }
      ]
    }


def solution_donut_chart(solutions, width, height):
  """Return a Vega description of a nested donut chart of sectors & solutions.
     Vega grammar: https://vega.github.io/vega/docs/

     Arguments:
       solutions: Pandas DataFrame with columns 'Solution', 'Sector', and 'CO2eq'
       width, height: in pixels
  """
  sectors = solutions.pivot_table(index='Sector', aggfunc=sum)
  solution_elements = {}
  sector_elements = {}
  idx = 1
  for row in solutions.itertuples(index=False):
    name = getattr(row, 'Solution')
    sector = getattr(row, 'Sector')
    co2eq = getattr(row, 'CO2eq')
    solution_elements[name] = {'id': idx, 'name': name, 'sector': sector, 'size': co2eq}
    idx += 1
  for row in sectors.sort_values(by=['CO2eq'], ascending=False).itertuples(index=True):
    name = getattr(row, 'Index')
    sector = getattr(row, 'Index')
    co2eq = getattr(row, 'CO2eq')
    sector_elements[name] = {'id': idx, 'name': name, 'sector': sector, 'size': co2eq}
    idx += 1

  return {
      "$schema": "https://vega.github.io/schema/vega/v4.json",
      "width": width,
      "height": height,
      "autosize": "none",

      "signals": [
    {
      "name": "startAngle", "value": 0,
    },
    {
      "name": "endAngle", "value": 6.29,
    },
    {
      "name": "padAngle", "value": 0,
    },
    {
      "name": "sort", "value": False,
    }
  ],

  "data": [
    {
      "name": "solutions",
      "values": list(solution_elements.values()),
      "transform": [
        {
          "type": "pie",
          "field": "size",
          "startAngle": {"signal": "startAngle"},
          "endAngle": {"signal": "endAngle"},
          "sort": {"signal": "sort"}
        }
      ]
    },
    {
      "name": "sectors",
      "values": list(sector_elements.values()),
      "transform": [
        {
          "type": "pie",
          "field": "size",
          "startAngle": {"signal": "startAngle"},
          "endAngle": {"signal": "endAngle"},
          "sort": {"signal": "sort"}
        }
      ]
    }
  ],

  "scales": [
    {
      "name": "color",
      "type": "ordinal",
      "domain": list(sector_colormap.keys()),
      "range": list(sector_colormap.values())
    },
  ],

  "marks": [
    {
      "type": "arc",
      "from": {"data": "solutions"},
      "encode": {
        "enter": {
          "fill": {"scale": "color", "field": "sector"},
          "x": {"signal": "width / 2"},
          "y": {"signal": "height / 2"},
          "tooltip": {"signal": "{title: datum.name, 'CO2eq': format(datum['size'], '.2f') + ' Gigatons'}"}
        },
        "update": {
          "startAngle": {"field": "startAngle"},
          "endAngle": {"field": "endAngle"},
          "padAngle": {"signal": "padAngle"},
          "innerRadius": {"value": 130},
          "outerRadius": {"value": 150},
          "cornerRadius": {"value": 0}
        }
      }
    },
    {
      "type": "arc",
      "from": {"data": "sectors"},
      "encode": {
        "enter": {
          "fill": {"scale": "color", "field": "sector"},
          "x": {"signal": "width / 2"},
          "y": {"signal": "height / 2"},
          "tooltip": {"signal": "{title: datum.name, 'CO2eq': format(datum['size'], '.2f') + ' Gigatons'}"}
        },
        "update": {
          "startAngle": {"field": "startAngle"},
          "endAngle": {"field": "endAngle"},
          "padAngle": {"signal": "padAngle"},
          "innerRadius": {"value": 98},
          "outerRadius": {"value": 118},
          "cornerRadius": {"value": 0}
        }
      }
    },
  ]
}
