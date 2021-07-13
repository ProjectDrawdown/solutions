from bqplot import LinearScale, OrdinalScale, Figure, Axis, Bars


def soln_comparison(df, title=None):
    """
    Returns an ordered horizontal bar chart comparing a given value over multiple solutions.
    Args:
        df: pandas DataFrame with solution names as the index and one column of numerical data
            (if there is more than one column it will plot the first one).
        title: Optional title for the chart

    Returns:
        bqplot Figure object
    """
    val_name = df.columns[0]
    df = df.sort_values(by=[val_name], ascending=False)
    title = f'{val_name} comparison' if title is None else title

    y_scale = LinearScale()
    y_axis = Axis(scale=y_scale, label=val_name, orientation='horizontal')
    x_scale = OrdinalScale()
    x_axis = Axis(scale=x_scale, grid_lines='none', orientation='vertical')
    bars = Bars(x=df.index.values, y=df[val_name].values,
                scales={'x': x_scale, 'y': y_scale}, orientation='horizontal')
    fig = Figure(marks=[bars], axes=[x_axis, y_axis], padding_y=0, title=title,
                 fig_margin={'top': 60, 'bottom': 60, 'left': 200, 'right': 60})
    return fig
