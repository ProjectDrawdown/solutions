import os
import pandas as pd
import ui.geo

def test_get_globe():
    df = pd.DataFrame(
            [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]],
            columns=['World', 'OECD90', 'Eastern Europe', 'Asia (Sans Japan)',
                'Middle East and Africa', 'Latin America', 'China', 'India', 'EU', 'USA'])
    _ = ui.geo.get_globe(topofile=os.path.join('data', 'world_topo_lowres.json'), df=df)
