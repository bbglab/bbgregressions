def create_metric_table(metric_df, metric_var, rows_var, cols_var,
                        rows_names, cols_names,
                        total_cols_by, total_rows_by,
                        metric_var4file, save_files_dir,
                        keep_rows_ordered = True, keep_cols_ordered = True,
                        missing_values = 'cohort'
                        ):
    """
    Converts metric_df in a pivoted table using
    metric_var, rows_var and cols_var. Saves this
    dataframe with columns as cols_names and
    index as rows_names, regardless of any of the
    provided names is not in metric_df (thus, that
    column/row is filled with NA). Orders rows and/or
    columns if indicated according to cols_names/rows_names
    order. Also, creates two dataframes with the totals
    of the rows and the columns, according to total_by_cols
    and total_by_rows. Keeps as well all cols_names and rows_names

    Parameters
    ----------
    metric_df: pandas Dataframe
        Initial dataframe with at least 3 columns named
        as provided in metric_var, rows_var, cols_var
    metric_var: str
        Column name for the values to be used to fill
        the pivoted dataframe
    rows_var: str
        Column name for the values to be used as row names
        of the pivoted dataframe
    cols_var: str
        Column name for the values to be used as column names
        of the pivoted dataframe
    rows_names: list
        List of values to be used as the row names of the
        pivoted dataframe. Used both to subset the df if needed
        and to add rows with NA we want to keep for downstream
        analysis
    cols_names: list
        List of values to be used as the column names of the
        pivoted dataframe. Used both to subset the df if needed
        and to add columns with NA we want to keep for downstream
        analysis
    total_cols_by: str
        How to calculate the total for the columns of the dataframe.
        If "sum", "mean" or "median", calculates the total from the
        main pivoted dataframe. If other value, the total is provided
        in metric_df and total_cols_by value should correspond with the
        value used in the specific metric_df to gather all the columns
        into one value.
    total_rows_by: str
        How to calculate the total for the rows of the dataframe.
        If "sum", "mean" or "median", calculates the total from the
        main pivoted dataframe. If other value, the total is provided
        in metric_df and total_rows_by value should correspond with the
        value used in the specific metric_df to gather all the rows
    metric_var4file: str
        Name to be used in the file naming for the metric.
        TODO: maybe provide a dictionary with the equivalences instead
        (this is for the regressions, for which the file name is
        informative)
    save_files_dir: str
        Path where to store the generated files
    keep_rows_ordered: Boolean (default: True)
        Whether to keep rows ordered as provided in row_names
        If False, orders alphabetically
    keep_cols_ordered: Boolean (default: True)
        Whether to keep columns ordered as provided in col_names
        If False, orders alphabetically

    Returns
    -------
    None
    """
    ## -- MAIN DATAFRAME -- ##
    # pivot and reindex so that it contains all col_names and rows_names
    metric_df_p = metric_df.pivot(values = metric_var,
                                  index = rows_var,
                                  columns = cols_var).reindex(index = rows_names,
                                                              columns = cols_names)

    # remove genes for which all the values are NA
    genes2remove = metric_df_p.loc[metric_df_p.isna().all(axis = 1)].index
    print("These genes will be removed from the analysis because no value was calculated:", genes2remove.tolist())
    metric_df_p = metric_df_p.dropna(how = 'all', axis=0)


    if missing_values == 'ignore':
        print("Not filling NAs with cohort value")

    elif missing_values == 'cohort':
        # fill NA with gene's cohort value
        metric_df_cohort = metric_df.pivot(values = metric_var,
                                        index = rows_var,
                                        columns = cols_var).reindex(index = rows_names,
                                                                    columns = ["all_samples"])
        metric_df_p = metric_df_p.apply(lambda col: col.fillna(metric_df_cohort["all_samples"]))
        print("Filling NAs with cohort value")

    elif missing_values == 'mean_samples':
        # fill NA with gene's mean
        metric_df_p = metric_df_p.apply(lambda row: row.fillna(row.mean()), axis = 1)
        print("Filling NAs with mean value")

    else:
        raise ValueError("Invalid missing values treatment")


    # Identify genes where all values in a row are the same
    genes_to_remove = metric_df_p.loc[metric_df_p.nunique(axis=1) == 1].index
    print("These genes will be removed from the analysis because all values are identical:", genes_to_remove.tolist())

    # Drop these rows from the dataframe
    metric_df_p = metric_df_p.loc[metric_df_p.nunique(axis=1) > 1]


    # reorder alphabetically if provided ordered is not kept
    if not keep_rows_ordered:
        metric_df_p = metric_df_p.sort_index(axis = 0)
    if not keep_cols_ordered:
        metric_df_p = metric_df_p.sort_index(axis = 1)

    ## -- TOTAL COLUMNS DATAFRAME -- ##
    # if sum, mean or median, calculate from the pivoted df
    if total_cols_by == "sum":
        metric_cols_total_df = metric_df_p.sum(axis = 0, skipna = True).to_frame(metric_var) #skipna=True to avoid getting NA as the total when there are NAs in the df
    elif total_cols_by == "mean":
        metric_cols_total_df = metric_df_p.mean(axis = 0, skipna = True).to_frame(metric_var)
    elif total_cols_by == "median":
        metric_cols_total_df = metric_df_p.median(axis = 0, skipna = True).to_frame(metric_var)
    # otherwise, get from metric_df
    else:
        metric_cols_total_df = metric_df.loc[(metric_df[rows_var] == total_cols_by)
                                            & (metric_df[cols_var].isin(cols_names))][[cols_var, metric_var]].set_index(
                                            cols_var).reindex(index = cols_names)
        ## reorder alphabetically if provided ordered is not kept
        if not keep_cols_ordered:
            metric_cols_total_df = metric_cols_total_df.sort_index(axis = 0)

    ## -- TOTAL ROWS DATAFRAME -- ##
    # if sum, mean or median, calculate from the pivoted df
    if total_rows_by == "sum":
        metric_rows_total_df = metric_df_p.sum(axis = 1, skipna = True).to_frame(metric_var)
    elif total_rows_by == "mean":
        metric_rows_total_df = metric_df_p.mean(axis = 1, skipna = True).to_frame(metric_var)
    elif total_rows_by == "median":
        metric_rows_total_df = metric_df_p.median(axis = 1, skipna = True).to_frame(metric_var)
    # otherwise, get from metric_df
    else:
        metric_rows_total_df = metric_df.loc[(metric_df[cols_var] == total_rows_by)
                                            & (metric_df[rows_var].isin(rows_names))][[rows_var, metric_var]].set_index(
                                            rows_var).reindex(index = rows_names)
        ## reorder alphabetically if provided ordered is not kept
        if not keep_rows_ordered:
            metric_rows_total_df = metric_rows_total_df.sort_index(axis = 0)

    ## -- SAVE OR RETURN -- ##
    metric_df_p.to_csv(os.path.join(save_files_dir, f"{metric_var4file.lower()}.tsv"), sep = "\t")
    # assert metric_df_p.shape == (len(rows_names), len(cols_names))
    metric_rows_total_df.to_csv(os.path.join(save_files_dir, f"{metric_var4file.lower()}.total_{rows_var.lower()}.tsv"), sep = "\t")
    # assert metric_rows_total_df.shape == (len(rows_names), 1)
    metric_cols_total_df.to_csv(os.path.join(save_files_dir, f"{metric_var4file.lower()}.total_{cols_var.lower()}.tsv"), sep = "\t") # having points here may collapse with the file naming in the main function
    # assert metric_cols_total_df.shape == (len(cols_names), 1)

    return None