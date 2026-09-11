
import math , pywt , numpy as np, pandas as pd
import scipy.stats as stats, scipy.signal as signal


def compute_grouped_mean(df, group_cols, group_cols_not_for_overall_mean, measure_col, 
                         measure_type='default', measure_type_attr={}, keepExactValues = False,
                         measure_out=None, 
                         additional_filters=None):
 
    print('[Deprecated] Use compute_grouped_stats')

    # Apply additional filters if provided
    if additional_filters:
        for key, value in additional_filters.items():
            if isinstance(value, list):
                df = df[df[key].isin(value)]
            else:
                df = df[df[key] == value]

    match measure_type:
        case 'AOIRunCount':
            # Group by group_cols and calculate the mean for each measure
            grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            
            # Drop participant and question columns from group columns and compute the mean
            overall_mean = grouped_means.groupby(group_cols,as_index=False)[[measure_col]].mean()
        case 'FixationCount':
            # Group by group_cols and calculate the mean for each measure
            grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            
            # Drop participant and question columns from group columns and compute the mean
            overall_mean = grouped_means.groupby(group_cols,as_index=False)[[measure_col]].mean()
        case 'prop':
            # Group by group_cols and calculate the mean for each measure
            if not('agg' in measure_type_attr.keys()):
                grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            else:
                _, grouped_means = compute_grouped_mean(
                    df,
                    group_cols, group_cols_not_for_overall_mean, 
                    measure_col, measure_type=measure_type_attr['agg'], 
                    measure_type_attr=measure_type_attr,
                    additional_filters=additional_filters)
            if keepExactValues: grouped_means[measure_col+'_exact'] = grouped_means[measure_col]

            # -> use .transform to return a dataset with the same index (i.e. same number of rows).
            if not('group_total_cols' in measure_type_attr.keys()):
                raise KeyError('This measure type requires "group_total_cols" as parameter in measure_type_attr')
            _tot = grouped_means.groupby(measure_type_attr['group_total_cols'])[[measure_col]].transform('sum')
            grouped_means[[measure_col]] = grouped_means[[measure_col]]/_tot[[measure_col]]
            
            # Drop participant and question columns from group columns and compute the mean
            overall_mean = grouped_means.groupby(group_cols,as_index=False)[[measure_col]].mean()
        case 'default':
            # /!\ this is NOT the default case /!\
            # Group by group_cols and calculate the mean for each measure
            grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].mean().reset_index()
            
            
            # Drop participant and question columns from group columns and compute the mean
            overall_mean = grouped_means.groupby(group_cols,as_index=False)[[measure_col]].mean()

        case default:
            raise KeyError(f"The following key ('{measure_type}') is unknown.")
    

    # Rename the output column (if necessary)
    if measure_out:
        grouped_means = grouped_means.rename(columns={measure_col: measure_out})
        overall_mean = overall_mean.rename(columns={measure_col: measure_out})
    
    return overall_mean, grouped_means



def compute_grouped_stats(df, group_cols, group_cols_not_for_overall_mean, measure_col, 
                         measure_type='default', measure_type_attr={}, keepExactValues = False,
                         measure_out=None, 
                         additional_filters=None):
    """
    Compute the stats on grouped data .    
    """
 
    # Apply additional filters if provided
    if additional_filters:
        for key, value in additional_filters.items():
            if isinstance(value, list):
                df = df[df[key].isin(value)]
            else:
                df = df[df[key] == value]

    grouped_stats = {"values":None, "means":None, "stds":None, "vars":None, "mins":None, "maxs":None}

    match measure_type:
        case 'AOIRunCount':
            # Group by group_cols and calculate the mean for each measure
            #grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()

            grouped_stats['values'] = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            grouped_stats['means'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].mean()
            grouped_stats['stds'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].std()
            grouped_stats['vars'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].var()
            grouped_stats['mins'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].min()
            grouped_stats['maxs'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].max()
          
            # Drop participant and question columns from group columns and compute the mean
            # overall_mean = grouped_stats['means']
        case 'FixationCount':
            # Group by group_cols and calculate the mean for each measure
            #grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()

            grouped_stats['values'] = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            grouped_stats['means'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].mean()
            grouped_stats['stds'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].std()
            grouped_stats['vars'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].var()
            grouped_stats['mins'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].min()
            grouped_stats['maxs'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].max()

            # Drop participant and question columns from group columns and compute the mean
            # overall_mean = grouped_stats['means']
        case 'prop':
            # Group by group_cols and calculate the mean for each measure
            if not('agg' in measure_type_attr.keys()):
                # grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
                grouped_values = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
            else:
                _s = compute_grouped_stats(
                    df,
                    group_cols, group_cols_not_for_overall_mean, 
                    measure_col, measure_type=measure_type_attr['agg'], 
                    measure_type_attr=measure_type_attr,
                    additional_filters=additional_filters)
                grouped_values = _s['values']
            if keepExactValues: grouped_values[measure_col+'_exact'] = grouped_values[measure_col]

            # -> use .transform to return a dataset with the same index (i.e. same number of rows).
            if not('group_total_cols' in measure_type_attr.keys()):
                raise KeyError('This measure type requires "group_total_cols" as parameter in measure_type_attr')
            _tot = grouped_values.groupby(measure_type_attr['group_total_cols'])[[measure_col]].transform('sum')
            grouped_values[[measure_col]] = grouped_values[[measure_col]]/_tot[[measure_col]]

            grouped_stats['values'] = grouped_values
            grouped_stats['means'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].mean()
            grouped_stats['stds'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].std()
            grouped_stats['vars'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].var()
            grouped_stats['mins'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].min()
            grouped_stats['maxs'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].max()
            
            # Drop participant and question columns from group columns and compute the mean
            # overall_mean = grouped_stats['means']
        case 'default':
            # /!\ this is NOT the default case /!\
            # Group by group_cols and calculate the mean for each measure
            # grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].mean().reset_index()

            grouped_stats['values'] = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].mean().reset_index()
            grouped_stats['means'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].mean()
            grouped_stats['stds'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].std()
            grouped_stats['vars'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].var()
            grouped_stats['mins'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].min()
            grouped_stats['maxs'] = grouped_stats['values'].groupby(group_cols,as_index=False)[[measure_col]].max()

            
            # Drop participant and question columns from group columns and compute the mean
            # overall_mean = grouped_stats['means']

        case default:
            raise KeyError(f"The following key ('{measure_type}') is unknown.")
    

    # Rename the output column (if necessary)
    if measure_out:
        for k in grouped_stats.keys():
            grouped_stats[k] = grouped_stats[k].rename(columns={measure_col: measure_out})
        # overall_mean = overall_mean.rename(columns={measure_col: measure_out})
    
    return grouped_stats





### SHOULD BE REMOVED
# This function remains to keep a track of the previous versions.
def compute_grouped_mean_AOIRunCount(df, group_cols, group_cols_not_for_overall_mean, measure_col, additional_filters=None):
 
    # Apply additional filters if provided
    if additional_filters:
        for key, value in additional_filters.items():
            df = df[df[key] == value]
 
    # Group by group_cols and calculate the mean for each measure
    grouped_means = df.groupby(group_cols+group_cols_not_for_overall_mean)[[measure_col]].count().reset_index()
    
    # Drop participant and question columns from group columns and compute the mean
    overall_mean = grouped_means.groupby(group_cols,as_index=False)[[measure_col]].mean()

    return overall_mean, grouped_means



def inferenceTest(df, 
                   groupCols, measure_col, aggregate_fct, 
                   conditionsCols, conditions, conditionsMergeOn,
                   mergeCols=None,
                   additional_filters=None, do_print=True):

    if mergeCols is None:
        mergeCols = groupCols

    # Apply additional filters if provided
    if additional_filters:
        for key, value in additional_filters.items():
            if isinstance(value, list):
                df = df[df[key].isin(value)]
            else:
                df = df[df[key] == value]
    

    # Group by group_cols and calculate the mean
    df = df.groupby(groupCols,as_index=False).agg({measure_col:aggregate_fct})
    
    #regroup by the first n elements of the group_calls and compute mean
    # to do: adjust later to consider only one data point per participant
    # now it is two data points per participant
    all_stats = []
    p_values = []
    n_values = []
    for cat1, cat2 in conditions:
                
        data_cat1 = df.loc[(df[conditionsCols]==cat1)][mergeCols+[measure_col]].dropna()
        data_cat2 = df.loc[(df[conditionsCols]==cat2)][mergeCols+[measure_col]].dropna()

        merged = data_cat1.merge(data_cat2, on=conditionsMergeOn, suffixes=('_cat1', '_cat2'), how='inner')
        

        n_merged = len(merged)
        merged_noz = merged.loc[~(merged[f'{measure_col}_cat1']==merged[f'{measure_col}_cat2']), :]
        n_merged_noz = len(merged_noz)

        if n_merged == 0:
            print('No sample (len = 0) to compare.')
            return float('nan'), [float('nan')], 0
        
        # if (1-(n_merged_noz/n_merged)) > 0.1:
        #     print('More than 10% of pairs of identical values.')
        #     print(f'{n_merged-n_merged_noz} out of {n_merged} pairs ({1-(n_merged_noz/n_merged):.2%}) have been removed.')
        # elif n_merged_noz != n_merged:
        #     print(f'N = {n_merged_noz} / {n_merged}')

        # Calculate Wilcoxon test
        stat, p = stats.wilcoxon(merged_noz[f'{measure_col}_cat1'], merged_noz[f'{measure_col}_cat2'])

        if do_print:
            ## Display in green if p < 0.05, else red:
            # color = 'green' if p < 0.05 else 'red'
            # display(HTML(f"<span style='color: {color};'>{cat1} vs {cat2}: p-value = {p}</span>"))
            print(f"{cat1} vs {cat2}: p-value = {p}")

        all_stats.append(stat)
        p_values.append(p)
        n_values.append(n_merged_noz)

    return all_stats, p_values, n_values



def inference_test(df, 
                   groupCols, measure_col, aggregate_fct, 
                   conditionsCols, conditions,
                   additional_filters=None, do_print=True):
    
    print('[Deprecated] Use InferenceTest')
    
    conditionsMergeOn = groupCols[:2]
    mergeCols = groupCols[:3]

    return inferenceTest(df,
                         groupCols, measure_col, aggregate_fct, 
                         conditionsCols, conditions, conditionsMergeOn,
                         mergeCols,
                         additional_filters, do_print)



###############################################################################
# End of file
#
def main_exec():
    print("--> Running main_exec function.\n")

def import_exec():
    print("--> Importing grouped_mean module file.\n")
 
if __name__ == "__main__": main_exec()
else: import_exec()