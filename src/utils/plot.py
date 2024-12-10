import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_normalized_positions(series, graph_title, n_bins=7):
    """
    Create a bar plot of binned averages along the length of an array,
    but plotted along an x-axis normalized to [0,1].

    Parameters:
    series: pandas.Series where each element is an array of numbers
    graph_titre: string with the name of the quantity plotted
    n_bins: number of bins to divide the [0,1] interval into
    """
    # Create empty lists to store normalized positions and values
    all_positions = []
    all_values = []

    # Process each array in the series
    for arr in series:
        length = len(arr)
        # Create normalized positions for this array
        positions = np.linspace(0, 1, length)

        all_positions.extend(positions)
        all_values.extend(arr)

    # Create a DataFrame with the normalized positions and values
    df = pd.DataFrame({
        'position': all_positions,
        'value': all_values
    })

    # Create bins and calculate statistics for each bin
    df['bin'] = pd.cut(df['position'], bins=n_bins, labels=[f'{i/n_bins:.2f}-{(i+1)/n_bins:.2f}' for i in range(n_bins)])

    bin_stats = df.groupby('bin', observed=True).agg({
        'value': ['mean']
    }).reset_index()

    # Flatten the column names
    bin_stats.columns = ['bin', 'mean']

    # Create the plot
    plt.figure(figsize=(8, 3))
    sns.barplot(data=bin_stats, x='bin', y='mean')

    plt.title(f'Average {graph_title} along normalized path distance')
    plt.xlabel('Normalized distance along the path')
    plt.ylabel('Average bits of information')
    plt.xticks(rotation=45)

    plt.gcf()
    plt.show()