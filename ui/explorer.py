import itertools
import numpy as np
import bokeh.plotting as bp
import bokeh.models as bm
from bokeh.palettes import Dark2_8


# Override these with your own functions if you want to do any of this differently.
def plot_setup( ):
    """Common initialization routine for bokeh plots"""
    p = bp.figure(tools="pan,box_zoom,reset")
    p.sizing_mode = "stretch_width"
    p.max_width = 1000
    p.yaxis.major_label_orientation = "vertical"
    p.toolbar.logo = None
    return p

def hover_tool( points ):
    """Return a bokeh HoverTool configured how we like it.  Return None to skip hovering entirely.
    Parameter: points: the set of point renderers (used to make hover only show data over these points)"""
    return bm.HoverTool(
        renderers=points,
        toggleable=False,
        tooltips="""<div style='padding:10px'>$name @Year{0}: @$name{0,0.00}</div>"""
    )


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

        # The following parameters control some styling aspects of plotting.
        # You can override them as you would like.
        self.colors = Dark2_8   # Colors for lines are taken from this sequence
        self.plot_setup = plot_setup
        self.hover_tool = hover_tool

    # A note on the plotting strategy used here: 
    # Our pandas dataframe has (scenario x year) for the row index
    # and region for the column index.  But we want to index by (scenario x region)
    # for the plot (that is, there should be a separate line for scenario and region).
    # No doubt there is some panda-foo that could re-arrange the indices of a
    # dataframe this way.  Instead we simply loop over the scenarios, and for
    # each scenario draw a line for each region.

    def show_co2_reduction(self, keep_zeros=False):

        # get the data from the solution
        co2_r_data = self.solution.co2_reduction()

        # plot it
        p = self.plot_setup()
        p.title="CO2 Equiv Reduction"
        p.yaxis.axis_label="Gigatons"
        colors = itertools.cycle(self.colors)

        points = []
        for i in range(self.scenario_count):

            sdata = co2_r_data.loc[i]  # data for the i'th scenario
            # One of those bits of code that makes things needlessly confusing....
            # Bokeh has certain limitations in how it can interact with data that is provided via multiple 
            # separate renderings, which we are doing below both with the circle and line, and over multiple 
            # scenarios/dataframes.  To make it easy to use other Bokeh functionality (like hover tooltips)
            # we re-name the individual scenario dataframe columns to embed the scenario number.
            # This is really a secondary bit of magic; ignore it the first time you read the code.
            sdata.columns = [ f's{i} - {c}' for c in sdata.columns ]

            # Now give it to Bokeh
            cds = bm.ColumnDataSource(sdata)    
            for c in sdata.columns:
                if keep_zeros or np.count_nonzero(sdata[c]) > 0:
                    color = next(colors)
                    p.line(x='Year', y=c, source=cds, color=color, legend_label=c )
                    points.append( p.circle(x='Year', y=c, source=cds, color=color, name=c, hit_dilation=2.5 ) )
        
        hv = self.hover_tool(points)
        if hv: 
            p.add_tools(hv)
        bp.show(p)

