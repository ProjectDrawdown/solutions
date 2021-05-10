import itertools
import numpy as np
import bokeh.plotting as bp
import bokeh.models as bm
from bokeh.palettes import Dark2_8

class SolutionExporer:
    """Creates pretty charts for solution."""
    # The plan is that the charts will share some common selections, so you
    # can focus on a scenario with one click, that kind of thing.
    # But for now, we'll just settle for showing you a chart

    def __init__(self, solution):
        """Creates an explorer for the provided solution.  Typical usage:
        from model import solution
        from ui import explorer

        mysolution = solution.Solution('bioplastic')
        explorer = explorer.SolutionExplorer(mysolution)
        explorer.show_co2_reduction()
        """
        self.solution = solution
        self.scenario_count = len(self.solution.scenario_names)

        # You can set this to any color sequence that you like.
        self.colors = Dark2_8
    

    # A note on the plotting strategy used here: 
    # Our pandas dataframe has (scenario x year) for the row index
    # and region for the column index.  But we want to index by (scenario x region)
    # for the plot (that is, there should be a separate line for scenario and region).
    # No doubt there is some panda-foo that could re-arrange the indices of a
    # dataframe this way.  Instead we simply loop over the scenarios, and for
    # each scenario draw a line for each region.

    def show_co2_reduction(self, keep_zeros=False):
        p = bp.figure()
        co2_r_data = self.solution.co2_reduction()
        cols = co2_r_data.columns
        colors = itertools.cycle(self.colors)
        for i in range(self.scenario_count):
            sdata = co2_r_data.loc[i]
            # ColumnDataSource tells bokeh how to format pandas data 
            cds = bm.ColumnDataSource(sdata)
            for c in sdata.columns:
                if keep_zeros or np.count_nonzero(sdata[c]) > 0:
                    p.line(x='Year', y=c, source=cds, legend_label=f's{i} - {c}', color=next(colors))
        bp.show(p)

