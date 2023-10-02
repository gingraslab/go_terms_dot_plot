import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.colors import LogNorm
import os
import warnings
warnings.filterwarnings('ignore')


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n))
    )
    return new_cmap


def process_files(directory: str, top_number: int = 5):
    # Iterate over files in the directory
    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            # Load the data
            file_path = os.path.join(directory, file)
            xls = pd.ExcelFile(file_path)
            
            # Dictionaries to hold dataframes
            dfs = {}
            
            # Load each sheet into a dataframe and keep top_number rows
            top_number = 5
            for sheet_name in xls.sheet_names:
                dfs[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
                dfs[sheet_name] = dfs[sheet_name].nsmallest(top_number, 'p-value')
                dfs[sheet_name]['Source'] = sheet_name
            
            # Concatenate all dataframes into one
            df = pd.concat(dfs.values())
            
            # Count the number of Genes for each term
            df['Genes'] = df['Genes'].str.split(',').str.len()
            
            # Create a colormap
            cmap = cm.get_cmap('Oranges_r')
            cmap = truncate_colormap(cmap, 0.0, 0.7)
            
            # Create a dictionary that maps p-values to colors
            color_dict = {p: cmap(i/15) for i, p in enumerate(sorted(df['p-value'].unique()))}
            
            # Create the plot
            fig, ax1 = plt.subplots(figsize=(3, 8))
            
            # Scatter plot
            sns.scatterplot(x='Source', y='Term', size='Genes', hue='p-value', data=df, palette=color_dict, sizes=(50, 250), ax=ax1)
            ax1.set_xlabel(None)


            for label in ax1.get_xticklabels():
                label.set_rotation(90)

            # Adjust the x-limits to include some buffer space
            ax1.set_xlim(-0.5, len(dfs)-0.5)
            
            # Create size legend
            sizes = [50, 100, 150, 200]
            labels = ['50', '100', '150', '200']
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markersize=s/15, 
                                          markerfacecolor='black', label=label) for s, label in zip(sizes, labels)]
            lgd = ax1.legend(handles=legend_elements, title='Genes', loc='upper left', bbox_to_anchor=(1,0.5))   


            # Get the minimum and maximum p-values from your data
            min_p = df['p-value'].min()
            max_p = df['p-value'].max()
            
            # Create a logarithmic normalization object based on these values
            norm = LogNorm(vmin=min_p, vmax=max_p)
            
            # Create colorbar
            fig.subplots_adjust(bottom=0.3)
            cax = plt.axes([0.2, 0.05, 0.6, 0.03])
            cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal')
            cb.set_label('p-values')
            
            results_dir = 'results'
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
    
            # Set title and display the plot
            ax1.set_title(file[:-5])
            plt.rcParams['svg.fonttype'] = 'none'
            plt.savefig(f'{results_dir}/{file[:-5]}.svg', format="svg", dpi=3000, bbox_extra_artists=(lgd,), bbox_inches='tight')
            plt.close()


if __name__ == "__main__":
    directory_input = input("Please enter the directory containing the Excel files: ")
    top_number_input = input("Please enter the number of top rows to keep based on 'p-value' (default is 5): ")

    try:
        top_number_input = int(top_number_input)
    except ValueError:
        print("Invalid input for top_number. Using the default value of 5.")
        top_number_input = 5

    process_files(directory_input, top_number_input)
