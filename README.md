# **GO Terms Dot Plot Visualizer**

This tool has been developed for visualizing the top (a desired number) Gene Ontology (GO) terms for different conditions for groups of genes, producing a dot plot that facilitates comprehensive analysis and comparison across conditions.

## **Getting Started**

## **Prerequisites**
To run the tool, you need Python 3.x and the following libraries:
- pandas
- numpy
- matplotlib
- seaborn

Install the required libraries using the following command:
```shell
pip install pandas numpy matplotlib seaborn
```

## **Running the Tool**

To run the tool, navigate to the main directory in your terminal and execute the following command:
```shell
python3 src/go_terms_dot_plot.py
```
The tool will prompt you to enter:
1. The directory containing the input Excel files.
2. The number of top terms you wish to extract based on 'p-value'.

### **Example:**
```shell
(base) Admin@Desktop% python3 src/go_terms_dot_plot.py
Please enter the directory containing the Excel files: data
Please enter the number of top rows to keep based on 'p-value' (default is 5): 3
```
The generated plots will be saved in the 'results' folder.

## **Input** 
The tool expects g:Profiler output in .xlsx format.
Each condition should be represented in a separate sheet within the Excel file.

## **Output**
The tool generates a dot plot with:

Top GO terms on the y-axis.
Conditions on the x-axis.
Size of dots representing the number of genes.
Darker color representing higher significance.


## **Sample Files and Results**
There are three sample input files in the 'data' directory for your reference.
Sample results are available in the 'results' directory.
# go_terms_dot_plot
