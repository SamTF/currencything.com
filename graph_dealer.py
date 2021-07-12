import pandas as pd
import matplotlib.pyplot as plt


def plot_networth(data: pd.DataFrame) -> str:
    # setting the graph size & foreground colour
    plt.figure(figsize=(8,6), dpi=150).patch.set_facecolor('black')

    # plotting the values 
    plt.plot(data.index, data['SIZE'], c='xkcd:hot pink', linewidth = 0)
    plt.fill_between(data.index, data['SIZE'], facecolor = 'xkcd:hot pink')     # filling the area under the line to make it look nice - > bloomberg.py

    # Titles
    plt.title('Networth Over Time',     fontdict={'fontname': 'Comic Sans MS', 'fontsize': 20, 'color': 'white'})
    plt.xlabel('# Of Trades',           fontdict={'fontname': 'Comic Sans MS', 'fontsize': 12, 'color': 'white'})
    plt.ylabel('₡urrency Things',       fontdict={'fontsize': 12, 'color': 'white'})

    # Customising Colours                        - background, borders, tick markers
    ax = plt.gca()                               # gets the axes somehow, i dunno what this does
    ax.set_facecolor('black')                    # background colour
    ax.spines['bottom'].set_color('white')       # x-axis border colour
    ax.spines['left'].set_color('white')         # y-axis border colour
    ax.tick_params(colors="white", labelsize=10) # colour and size of the tick markers

    # Amount of ticks
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # sets a maximum amount of 6 ticks on the X Axis

    # Saving the graph as an SVG
    file_name = 'static/graphs/networth.svg'
    plt.savefig(file_name, transparent=True)

    return file_name


def plot_line_chart(data: pd.DataFrame, title: str, xlabel: str = '# Of Trades', ylabel: str = '₡urrency Things') -> str:
    '''
    Generic plotting function for a line chart. Plots a DataFrame with the index as the X values and the SIZE column as the Y values.
    Save the graph as an SVG and returns the its file name.

    data: Pandas DataFrame with the values to plot. Must contain a SIZE column.
    title: The title of the graph.
    xlabel: Label for the X-axis.
    ylabel: Label for the Y-axis.
    '''
    # setting the graph size
    plt.figure(figsize=(8,6), dpi=150)

    # plotting the values 
    plt.plot(data.index, data['SIZE'], c='xkcd:hot pink', linewidth = 0)
    plt.fill_between(data.index, data['SIZE'], facecolor = 'xkcd:hot pink')     # filling the area under the line to make it look nice - > bloomberg.py

    # Titles
    plt.title(title,    fontdict={'fontname': 'Comic Sans MS', 'fontsize': 20, 'color': 'white'})
    plt.xlabel(xlabel,  fontdict={'fontname': 'Comic Sans MS', 'fontsize': 12, 'color': 'white'})
    plt.ylabel(ylabel,  fontdict={'fontsize': 12, 'color': 'white'})

    # Customising Colours                        - background, borders, tick markers
    ax = plt.gca()                               # gets the axes somehow, i dunno what this does
    ax.set_facecolor('black')                    # background colour
    ax.spines['bottom'].set_color('white')       # x-axis border colour
    ax.spines['left'].set_color('white')         # y-axis border colour
    ax.tick_params(colors="white", labelsize=10) # colour and size of the tick markers

    # Amount of ticks
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # sets a maximum amount of 6 ticks on the X Axis

    # Saving the graph as an SVG
    file_name = 'static/graphs/line_chart.svg'
    plt.savefig(file_name, transparent=True)

    return file_name
