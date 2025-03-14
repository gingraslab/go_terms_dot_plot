import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.colors import LogNorm
import os
import warnings
import matplotlib
import re
import sys
warnings.filterwarnings('ignore')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
matplotlib.rcParams['figure.dpi'] = 300
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial']




def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n))
    )
    return new_cmap


# Create a scaling function based on your specific needs
def scale_sizes(sizes, base_size=200):
    max_size = sizes.max()
    return (sizes / max_size) * base_size

def process_file(GO_file: str, directory: str, top_number: int = 15, term_size_cutoff: int = 500, p_value_threshold: int = 0.05, filled_version: bool = True, multiquery: bool = False):
    # Load the data
    file_path = os.path.join(directory, GO_file)
    
    if multiquery:
        try:
            multiquery_df = pd.read_csv(file_path, sep=',', index_col=False)
            groups = []
            for col in multiquery_df.columns:
                x = re.search("(?<=adjusted_p_value__)(.*)", col)
                if x:
                    groups.append(x.group())
        except ValueError:
            sys.exit("Invalid structure for a multiquery search result.")
        except FileNotFoundError:
            sys.exit("File not found.")
        
    else:
        try:
            xls = pd.ExcelFile(file_path)
        except ValueError:
            sys.exit("Invalid structure for a GO search result.")
        except FileNotFoundError:
            sys.exit("File not found.")
        
    # Dictionaries to hold dataframes
    dfs = {}
    terms_to_show = []

    # Filled or unfilled version
    if filled_version:
        if multiquery:
            # Split groups
            for x in groups:
                #Adjust naming of columns
                df = multiquery_df[['source', 'term_name', 'term_id', 'term_size',
                                    'adjusted_p_value__' + x, 'query_size__' + x,
                                    'intersection_size__' + x]]
                df.columns = ['source', 'term_name', 'term_id', 'term_size',
                              'adjusted_p_value', 'query_size', 'intersection_size']      
                # Filter based on term_size and adjusted_p_value
                df = df.loc[(df['term_size'] <= term_size_cutoff) & (df['adjusted_p_value'] <= p_value_threshold)]
                # Find top terms by adjusted_p_value to include in terms_to_show.
                top_terms = df.nsmallest(top_number, 'adjusted_p_value')['term_name']
                terms_to_show = np.unique(np.append(terms_to_show, top_terms))
                # Store the processed dataframe
                dfs[x] = df
                
            for x in groups:
                #Access sheet
                df = dfs[x]
                # Keep only rows where term_name is in terms_to_show
                df = df.loc[df['term_name'].isin(terms_to_show)]
                # Sort by adjusted_p_value
                df = df.sort_values(by="adjusted_p_value")
                # Add sourceData column
                df['sourceData'] = x
                # Store the processed dataframe
                dfs[x] = df
        else:
            for sheet_name in xls.sheet_names:
                # Read sheet
                df = pd.read_excel(xls, sheet_name=sheet_name)
                # Filter based on term_size and adjusted_p_value
                df = df.loc[(df['term_size'] <= term_size_cutoff) & (df['adjusted_p_value'] <= p_value_threshold)]
                # Find top terms by adjusted_p_value to include in terms_to_show
                top_terms = df.nsmallest(top_number, 'adjusted_p_value')['term_name']
                terms_to_show = np.unique(np.append(terms_to_show, top_terms))
                # Store the processed dataframe
                dfs[sheet_name] = df                
                
            for sheet_name in xls.sheet_names:
                # Access sheet
                df = dfs[sheet_name]
                # Keep only rows where term_name is in terms_to_show
                df = df.loc[df['term_name'].isin(terms_to_show)]
                # Sort by adjusted_p_value
                df = df.sort_values(by="adjusted_p_value")
                # Add sourceData column
                df['sourceData'] = sheet_name
                # Store the processed dataframe
                dfs[sheet_name] = df
    else:
        if multiquery:
            # Split groups
            for x in groups:
                df = multiquery_df[['source', 'term_name', 'term_id', 'term_size',
                                    'adjusted_p_value__' + x, 'query_size__' + x,
                                    'intersection_size__' + x]]
                df.columns = ['source', 'term_name', 'term_id', 'term_size',
                              'adjusted_p_value', 'query_size', 'intersection_size']                
                # Filter based on term_size and adjusted_p_value
                df = df.loc[(df['term_size'] <= term_size_cutoff) & (df['adjusted_p_value'] <= p_value_threshold)]
                # Keep only the top_number of terms by adjusted_p_value
                df = df.nsmallest(top_number, 'adjusted_p_value')
                # Add sourceData column
                df['sourceData'] = x
                # Store the processed dataframe
                dfs[x] = df
        else:
            for sheet_name in xls.sheet_names:
                # Read sheet
                df = pd.read_excel(xls, sheet_name=sheet_name)
                # Filter based on term_size and adjusted_p_value
                df = df.loc[(df['term_size'] <= term_size_cutoff) & (df['adjusted_p_value'] <= p_value_threshold)]
                # Keep only the top_number of terms by adjusted_p_value
                df = df.nsmallest(top_number, 'adjusted_p_value')
                # Add sourceData column
                df['sourceData'] = sheet_name
                # Store the processed dataframe
                dfs[sheet_name] = df

    # Concatenate all dataframes into one
    df = pd.concat(dfs.values())

    # Shorten term name sizes if longer than 50 characters
    df["term_name"] = [term[:50] + "..." if len(term) > 50 else term for term in df["term_name"]] 
    
    # # Count the number of intersections for each term
    # df['intersections'] = df['intersections'].str.split(',').str.len()

    # Create a colormap
    cmap = cm.get_cmap('Oranges_r')
    cmap = truncate_colormap(cmap, 0.0, 0.7)

    # Create a dictionary that maps p-values to colors
    color_dict = {p: cmap(i/15) for i, p in enumerate(sorted(df['adjusted_p_value'].unique()))}

    # Create the plot
    # fig, ax1 = plt.subplots(figsize=(2, 15))
     # Determine the number of unique terms to display
    unique_terms_count = len(df['term_name'].unique())
    unique_conditions_count = len(df['sourceData'].unique())
    
    # Dynamically set the figure height based on the number of unique terms, 
    # and width based on the number of unique conditions
    # Assuming 0.4 inches per term and condition for readability
    dynamic_fig_height = max(5, unique_terms_count * 0.4)  # Ensuring a minimum height of 5 inches
    dynamic_fig_width = max(5, unique_conditions_count * 0.4)  # Ensuring a minimum width of 5 inches
    
    # Create the plot with dynamic figure size
    # fig, ax1 = plt.subplots(figsize=(8, dynamic_fig_height))  # Adjust the width as needed
    #fig, ax1 = plt.subplots(figsize=(3,9))
    #fig, ax1 = plt.subplots(figsize=(3,dynamic_fig_height))
    fig, ax1 = plt.subplots(figsize=(dynamic_fig_width,dynamic_fig_height))

    # Scatter plot
    # sns.scatterplot(x='sourceData', y='term_name', size='intersection_size', hue='adjusted_p_value', data=df, palette=color_dict, sizes=(20, 100), ax=ax1)
    # The sizes parameter in sns.scatterplot expects sizes in points^2
    max_size = df['intersection_size'].max()
    size_reference = 200  # This size corresponds to the max 'intersection_size' in points^2
    scatter_size_mapping = {i: (i / max_size) * size_reference for i in df['intersection_size'].unique()}

    # Use this mapping for the scatter plot sizes
    #sns.scatterplot(x='sourceData', y='term_name', size='intersection_size', hue='adjusted_p_value',
                    #data=df, palette=color_dict, sizes=scatter_size_mapping, ax=ax1)

    
    ax1.set_xlabel(None)

    for label in ax1.get_xticklabels():
        label.set_rotation(90)

    # Adjust the x-limits to include some buffer space
    ax1.set_xlim(-0.5, len(dfs)-0.5)
    
    # Adjust the y-axis limits
    ax1.set_ylim([-1, unique_terms_count])  

    #     # Determine the legend sizes based on the data
    # max_genes = df['intersection_size'].max()

    # # If max gene count is below 50, use the first set of sizes; otherwise, use the second set
    # if max_genes <= 50:
    #     legend_sizes = [1, 5, 10, 50]
    # else:
    #     legend_sizes = [50, 100, 150, 200]

    # # Calculate the markersizes for the legend, making the largest legend size proportionally larger
    # legend_markersizes = [(size / max_genes) * size_reference for size in legend_sizes]

    # # Create size legend
    # legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
    #                             markersize=np.sqrt(size),  # Size is in points^2, so take sqrt for diameter
    #                             markerfacecolor='black', label=str(legend_label)) 
    #                 for size, legend_label in zip(legend_markersizes, legend_sizes)]
    # lgd = ax1.legend(handles=legend_elements, title='Genes', loc='upper left', bbox_to_anchor=(1, 1), labelspacing=2.5)

    # Calculate scaled sizes for the plot
    max_size = df['intersection_size'].max()
    df['scaled_intersection_size'] = (df['intersection_size'] / max_size) * 200  # Scale sizes proportionally

    # Create a sizes dictionary that maps every unique scaled size to a specific plot size
    unique_scaled_sizes = df['scaled_intersection_size'].unique()
    sizes_dict = {size: size for size in unique_scaled_sizes}

    # Create the scatter plot using the sizes dictionary
    sns.scatterplot(x='sourceData', y='term_name', size='scaled_intersection_size', hue='adjusted_p_value',
                    data=df, palette=color_dict, sizes=sizes_dict, ax=ax1)

    # Calculate the smallest and largest sizes for the legend
    smallest_size_scaled = df['scaled_intersection_size'].min()
    largest_size_scaled = df['scaled_intersection_size'].max()

    # Create size legend with exact plot sizes
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                  markersize=np.sqrt(size),  # Convert area size to diameter
                                  markerfacecolor='black', label=f'{int(df[df["scaled_intersection_size"] == size]["intersection_size"].iloc[0])}') 
                      for size in [smallest_size_scaled, largest_size_scaled]]
    lgd = ax1.legend(handles=legend_elements, title='Intersection Size', loc='upper left', bbox_to_anchor=(1, 1), labelspacing=2.5)

    # Get the minimum and maximum adjusted p-values
    min_p = df['adjusted_p_value'].min()
    max_p = df['adjusted_p_value'].max()

    # Create a logarithmic normalization object based on these values
    norm = LogNorm(vmin=min_p, vmax=max_p)

    # Calculate the middle value for the p-value range on a log scale
    middle_p = np.sqrt(min_p * max_p)

    # Create colorbar with three ticks: min, middle, and max p-values
    fig.subplots_adjust(bottom=0.3)
    
    cax = fig.add_axes([ax1.get_position().x0, ax1.get_position().y0 - 0.15, ax1.get_position().width, 0.03])
    cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal', 
                    ticks=[min_p, middle_p, max_p])
    cb.set_label('adjusted_p_value')

    # Set the tick labels, using scientific notation
    cb.ax.set_xticklabels([f'$10^{{{int(np.log10(t))}}}$' for t in [min_p, middle_p, max_p]])

    # Prepare results directory
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Set title and display the plot
    plot_title = re.search("(.*)(?=\\.)", GO_file).group()
    ax1.set_title(plot_title)
    plt.rcParams['svg.fonttype'] = 'none'
    file_suffix = '_filled_' if filled_version else '_'
    plt.savefig(f'{results_dir}/{plot_title}{file_suffix}{term_size_cutoff}termsize.svg', dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')
    plt.savefig(f'{results_dir}/{plot_title}{file_suffix}{term_size_cutoff}termsize.png', dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')   
    plt.savefig(f'{results_dir}/{plot_title}{file_suffix}{term_size_cutoff}termsize.pdf', dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')    
    plt.close()

if __name__ == "__main__":
    # Dictionary to map string values to boolean
    bool_map = {"true": True, "false": False}
    
    directory_input = input("Please enter the directory: ")
    file_input = input("Please enter the name of the GO file: ")
    top_number_input = input("Please enter the number of top rows to keep based on 'adjusted_p_value' (default is 15): ")
    term_size_cutoff_input = input("Please enter the term size cutoff (default is 500): ")
    p_value_input = input("Please enter the adjusted p-value cutoff (default is 0.05): ")
    filled_version_input = input("Please enter 'True' for filled version or 'False' for unfilled version (default is True): ")
    multiquery_input = input("Please enter 'True' if this was a multiquery search or 'False' if every group was independently searched (default is False): ")

    try:
        top_number_input = int(top_number_input)
    except ValueError:
        print("Invalid input for top_number. Using the default value of 15.")
        top_number_input = 15

    try:
        term_size_cutoff_input = int(term_size_cutoff_input)
    except ValueError:
        print("Invalid input for term size cutoff. Using the default value of 500.")
        term_size_cutoff_input = 500
        
    try:
        p_value_input = float(p_value_input)
    except ValueError:
        print("Invalid input for p-value cutoff. Using the default value of 0.05.")
        p_value_input = 0.05

    try:
        ## Dictionary to map string values to boolean
        #bool_map = {"true": True, "false": False}
        filled_version_input = bool_map[filled_version_input.strip().lower()]
    except KeyError:
        print("Invalid input for filled version. Using the default value of True.")
        filled_version_input = True
    
    try:
        #multiquery_input = multiquery_input.strip().lower() == 'true'
        multiquery_input = bool_map[multiquery_input.strip().lower()]
    except KeyError:
        print("Invalid input for multiquery. Using the default value of False.")
        multiquery_input = False    

    process_file(GO_file = file_input, directory = directory_input, 
                 top_number = top_number_input, 
                 term_size_cutoff = term_size_cutoff_input, 
                 p_value_threshold = p_value_input, 
                 filled_version = filled_version_input, 
                 multiquery = multiquery_input)
