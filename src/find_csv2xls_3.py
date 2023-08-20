import os
# import pandas as pd
from pandas import read_csv, read_excel, concat, DataFrame
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import re
# import csv
# import xlsxwriter

default_config_file = os.getcwd().replace('\\', '/') + '/new.cfg'

search_errors = []


def search_csv(csv_file, search_query, export_folder, usecols=[]):
    # Initialize an empty list to store matching rows
    print('search_query', search_query)
    matching_rows = []

    # Use pandas chunksize parameter to read the CSV file in smaller chunks
    chunksize = 1000  # You can adjust this value based on available RAM
    if usecols:
        for chunk in read_csv(csv_file, sep=',', chunksize=chunksize, quotechar='"', quoting=1, escapechar='\\', usecols=usecols, dtype=str):
            #    for chunk in pd.read_csv(csv_file, sep=',', chunksize=chunksize, quotechar='"', quoting=csv.QUOTE_ALL):
            # Use DataFrame query to filter rows efficiently
            query = " & ".join(f"({condition})" for condition in search_query)
            matching_chunk = chunk.query(query)
            matching_rows.append(matching_chunk)
    else:
        for chunk in read_csv(csv_file, sep=',', chunksize=chunksize, quotechar='"', quoting=1, escapechar='\\', dtype=str):
            #    for chunk in pd.read_csv(csv_file, sep=',', chunksize=chunksize, quotechar='"', quoting=csv.QUOTE_ALL):
            # Use DataFrame query to filter rows efficiently
            query = " & ".join(f"({condition})" for condition in search_query)
            matching_chunk = chunk.query(query)
            matching_rows.append(matching_chunk)

    # Concatenate all the matching chunks into a single DataFrame
    result_df = concat(matching_rows, ignore_index=True)

    unique_name = output_format_input.get()

    # Export the results to a new CSV file in the export folder
    if output_format_options.get() == 'csv':
        export_filename = f"{unique_name}{os.path.basename(csv_file).replace('.csv', '')}_SearchResults.csv"
    else:
        export_filename = f"{unique_name}{os.path.basename(csv_file).replace('.csv', '')}_SearchResults.xlsx"

    export_file = os.path.join(os.path.dirname(csv_file), export_filename)

    if output_format_options.get() == 'csv':
        result_df.to_csv(export_file, index=False)
    else:
        result_df.to_excel(export_file, index=False)

    print('result_df', result_df)

    return export_file, len(result_df)


def search_excel(excel_file, search_query, export_folder, usecols=[]):
    # Initialize an empty list to store matching rows
    print('search_query', search_query)
    matching_rows = []

    df_excel = DataFrame()

    file_extension = os.path.splitext(excel_file)[-1].lower()
    engine = 'openpyxl' if file_extension == '.xlsx' else 'xlrd'

    if usecols:
        df_excel = read_excel(excel_file, usecols=usecols,
                              dtype=str, engine=engine)
    else:
        df_excel = read_excel(excel_file, dtype=str, engine=engine)

    query = " & ".join(f"({condition})" for condition in search_query)
    print('query:', query)
    matching_excel = df_excel.query(query)
    matching_rows.append(matching_excel)

    # Concatenate all the matching chunks into a single DataFrame
    result_df = concat(matching_rows, ignore_index=True)
    print('result_df:', result_df)

    unique_name = output_format_input.get()

    # Construct the export filename for both CSV and Excel formats
    base_filename = os.path.splitext(os.path.basename(excel_file))[0]
    if output_format_options.get() == 'csv':
        export_filename = f"{unique_name}{base_filename}_SearchResults.csv"
        export_file = os.path.join(export_folder, export_filename)
        result_df.to_csv(export_file, index=False)
    else:
        export_filename = f"{unique_name}{base_filename}_SearchResults.xlsx"
        export_file = os.path.join(export_folder, export_filename)
        result_df.to_excel(export_file, index=False)

    print('Exported to:', export_file)

    return export_file, len(result_df)


def browse_folder():
    folder_path = filedialog.askdirectory()  # Select a folder
    if folder_path:
        folder_entry.delete(0, tk.END)  # Clear the entry widget
        folder_entry.insert(0, folder_path)  # Insert the selected file path
        populate_column_options()  # You can define this function to populate columns


def get_columns_filter(config_file):
    all_columns_list = []
    if default_config_file != config_file:
        cfg_in = open(config_file)
        for line in cfg_in.readlines():
            rline = re.search('^(.+)$', line)
            if rline:
                column = rline.group(1)
                all_columns_list.append(column)
        cfg_in.close()

    return all_columns_list


def browse_fields_filter():
    config_file = filedialog.askopenfilename(initialdir=os.getcwd(),
                                             title="Select a Config file",
                                             filetypes=(("cfg files",
                                                         "*.cfg*"),
                                                        ("all files",
                                                         "*.*")))
    if config_file:

        all_columns_list = get_columns_filter(config_file)

        # Set the first column as the default
        column1_options.set(all_columns_list[0])
        # Set the first column as the default
        column2_options.set(all_columns_list[0])
        # Set the first column as the default
        column3_options.set(all_columns_list[0])
        # Set the first column as the default
        column4_options.set(all_columns_list[0])
        # Set the first column as the default
        column5_options.set(all_columns_list[0])

        column1_dropdown["menu"].delete(
            0, tk.END)  # Clear the existing options
        column2_dropdown["menu"].delete(
            0, tk.END)  # Clear the existing options
        column3_dropdown["menu"].delete(
            0, tk.END)  # Clear the existing options
        column4_dropdown["menu"].delete(
            0, tk.END)  # Clear the existing options
        column5_dropdown["menu"].delete(
            0, tk.END)  # Clear the existing options

        for column in all_columns_list:
            column1_dropdown["menu"].add_command(
                label=column, command=tk._setit(column1_options, column))
            column2_dropdown["menu"].add_command(
                label=column, command=tk._setit(column2_options, column))
            column3_dropdown["menu"].add_command(
                label=column, command=tk._setit(column3_options, column))
            column4_dropdown["menu"].add_command(
                label=column, command=tk._setit(column4_options, column))
            column5_dropdown["menu"].add_command(
                label=column, command=tk._setit(column5_options, column))


def execute_search():
    global search_errors
    # Clear previous errors
    search_errors = []
    error_text.delete(1.0, tk.END)  # Clear the error text box

    folder_path = folder_entry.get()
    config_file = default_config_file
    column1 = column1_options.get()
    value1 = value1_entry.get()
    column2 = column2_options.get()
    value2 = value2_entry.get()
    column3 = column3_options.get()
    value3 = value3_entry.get()
    column4 = column4_options.get()
    value4 = value4_entry.get()
    column5 = column5_options.get()
    value5 = value5_entry.get()
    column6 = column6_options.get()
    value6 = value6_entry.get()
    column7 = column7_options.get()
    value7 = value7_entry.get()
    column8 = column8_options.get()
    value8 = value8_entry.get()

    if not folder_path or not column1 or not value1:
        messagebox.showwarning("Missing Information",
                               "Please provide all the required information.")
        return

    # Define total_rows here
    total_rows = 0
    export_files = []

    # Get the selected logic (AND or OR)
    selected_logic = logic_var.get()

    # Get the directory path and the file name from the selected file path
    directory_path = os.path.dirname(folder_path)
    file_name = os.path.basename(folder_path)
    print(file_name)

    # Initialize the lists to store CSV and Excel files
    csv_files = []
    excel_files = []

    # Find all CSV and Excel files in the folder and its subdirectories
    csv_files = [file for file in os.listdir(
        folder_path) if file.lower().endswith('.csv')]
    excel_files = [file for file in os.listdir(folder_path) if file.lower(
    ).endswith('.xls') or file.lower().endswith('.xlsx')]

    # Check if the selected file is a CSV file
    if file_name.endswith(".csv"):
        csv_files.append(folder_path)
    # Check if the selected file is an Excel file
    elif file_name.endswith(".xls") or file_name.endswith(".xlsx"):
        excel_files.append(folder_path)

    # Display a message if no CSV or Excel files are found
    if not csv_files and not excel_files:
        messagebox.showinfo("No CSV or Excel Files",
                            "The selected file is not a CSV or Excel file.")
        return

    for csv_file in csv_files:
        print(csv_file)
        csv_file = folder_path + "/" + csv_file
        print(csv_file)
        export_file = ''
        try:
            columns_filter = get_columns_filter(config_file)

            # Define search queries based on selected logic
            if selected_logic == "AND":
                query_list = []

                if value1:
                    if search_type1_var.get() == "contains":
                        query_list.append(
                            f"`{str(column1)}`.str.contains('{value1}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{str(column1)}.str.lower() == '{value1.lower()}'")

                if value2 and column2:
                    if search_type2_var.get() == "contains":
                        query_list.append(
                            f"`{column2}`.str.contains('{value2}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column2}.str.lower() == '{value2.lower()}'")

                if value3:
                    if search_type3_var.get() == "contains":
                        query_list.append(
                            f"`{column3}`.str.contains('{value3}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column3}.str.lower() == '{value3.lower()}'")
                if value4 and column4:
                    if search_type4_var.get() == "contains":
                        query_list.append(
                            f"`{column4}`.str.contains('{value4}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column4}.str.lower() == '{value4.lower()}'")

                if value5 and column5:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column5}`.str.contains('{value5}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column5}.str.lower() == '{value5.lower()}'")
                if value6 and column6:
                    if search_type6_var.get() == "contains":
                        query_list.append(
                            f"`{column6}`.str.contains('{value6}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column6}.str.lower() == '{value6.lower()}'")
                if value7 and column7:
                    if search_type7_var.get() == "contains":
                        query_list.append(
                            f"`{column7}`.str.contains('{value7}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column7}.str.lower() == '{value7.lower()}'")
                if value8 and column8:
                    if search_type7_var.get() == "contains":
                        query_list.append(
                            f"`{column8}`.str.contains('{value8}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column8}.str.lower() == '{value8.lower()}'")

                combined_query = " & ".join(query_list)
                export_file, rows_found = search_csv(
                    csv_file, [combined_query], folder_path, columns_filter)
                total_rows += rows_found
            else:  # "OR" logic
                query_list = []

                if value1:
                    if search_type1_var.get() == "contains":
                        query_list.append(
                            f"`{column1}`.str.contains('{value1}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column1}.str.lower() == '{value1.lower()}'")

                if value2 and column2:
                    if search_type2_var.get() == "contains":
                        query_list.append(
                            f"`{column2}`.str.contains('{value2}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column2}.str.lower() == '{value2.lower()}'")

                if value3 and column3:
                    if search_type3_var.get() == "contains":
                        query_list.append(
                            f"`{column3}`.str.contains('{value3}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column3}.str.lower() == '{value3.lower()}'")
                if value4 and column4:
                    if search_type4_var.get() == "contains":
                        query_list.append(
                            f"`{column4}`.str.contains('{value4}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column4}.str.lower() == '{value4.lower()}'")

                if value5 and column5:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column5}`.str.contains('{value5}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column5}.str.lower() == '{value5.lower()}'")
                if value6 and column6:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column6}`.str.contains('{value6}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column6}.str.lower() == '{value6.lower()}'")
                if value7 and column7:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column7}`.str.contains('{value7}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column7}.str.lower() == '{value7.lower()}'")
                if value8 and column8:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column8}`.str.contains('{value8}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column8}.str.lower() == '{value8.lower()}'")

                if query_list:
                    combined_query = " | ".join(query_list)
                    export_file, rows_found = search_csv(
                        csv_file, [combined_query], folder_path, columns_filter)
                    total_rows += rows_found

        except Exception as e:
            error_message = f"Error: {str(e)}"
            log_error(error_message)

    for excel_file in excel_files:
        excel_file = folder_path + "/" + excel_file
        export_file = ''
        try:
            columns_filter = get_columns_filter(config_file)

            # Define search queries based on selected logic
            if selected_logic == "AND":
                query_list = []

                if value1:
                    if search_type1_var.get() == "contains":
                        query_list.append(
                            f"`{column1}`.str.contains('{value1}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column1}.str.lower() == '{value1.lower()}'")

                if value2 and column2:
                    if search_type2_var.get() == "contains":
                        query_list.append(
                            f"`{column2}`.str.contains('{value2}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column2}.str.lower() == '{value2.lower()}'")

                if value3:
                    if search_type3_var.get() == "contains":
                        query_list.append(
                            f"`{column3}`.str.contains('{value3}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column3}.str.lower() == '{value3.lower()}'")
                if value4 and column4:
                    if search_type4_var.get() == "contains":
                        query_list.append(
                            f"`{column4}`.str.contains('{value4}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column4}.str.lower() == '{value4.lower()}'")

                if value5 and column5:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column5}`.str.contains('{value5}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column5}.str.lower() == '{value5.lower()}'")
                if value6 and column6:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column6}`.str.contains('{value6}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column6}.str.lower() == '{value6.lower()}'")
                if value7 and column7:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column7}`.str.contains('{value7}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column7}.str.lower() == '{value7.lower()}'")
                if value8 and column8:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column8}`.str.contains('{value8}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column8}.str.lower() == '{value8.lower()}'")

                combined_query = " & ".join(query_list)
                export_file, rows_found = search_excel(
                    excel_file, [combined_query], folder_path, columns_filter)
                total_rows += rows_found

            else:  # "OR" logic
                query_list = []

                if value1:
                    if search_type1_var.get() == "contains":
                        query_list.append(
                            f"`{column1}`.str.contains('{value1}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column1}.str.lower() == '{value1.lower()}'")

                if value2 and column2:
                    if search_type2_var.get() == "contains":
                        query_list.append(
                            f"`{column2}`.str.contains('{value2}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column2}.str.lower() == '{value2.lower()}'")

                if value3 and column3:
                    if search_type3_var.get() == "contains":
                        query_list.append(
                            f"`{column3}`.str.contains('{value3}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column3}.str.lower() == '{value3.lower()}'")
                if value4 and column4:
                    if search_type4_var.get() == "contains":
                        query_list.append(
                            f"`{column4}`.str.contains('{value4}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column4}.str.lower() == '{value4.lower()}'")

                if value5 and column5:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column5}`.str.contains('{value5}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column5}.str.lower() == '{value5.lower()}'")
                if value6 and column6:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column6}`.str.contains('{value6}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column6}.str.lower() == '{value6.lower()}'")
                if value7 and column7:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column7}`.str.contains('{value7}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column7}.str.lower() == '{value7.lower()}'")
                if value8 and column8:
                    if search_type5_var.get() == "contains":
                        query_list.append(
                            f"`{column8}`.str.contains('{value8}', case=False, na=False)")
                    else:  # "exact match"
                        query_list.append(
                            f"{column8}.str.lower() == '{value8.lower()}'")

                if query_list:
                    combined_query = " | ".join(query_list)
                    export_file, rows_found = search_excel(
                        excel_file, [combined_query], folder_path, columns_filter)
                    total_rows += rows_found

        except Exception as e:
            error_message = f"Error: {str(e)}"
            log_error(error_message)

    # Display separate messages if CSV or Excel files are processed
    if len(csv_files) > 0 and len(excel_files) > 0:
        messagebox.showinfo(
            "Search Completed", f"Search completed for {len(csv_files)} CSV file(s) and {len(excel_files)} Excel file(s).\nTotal rows exported: {total_rows}")
        output_format_input.delete(0, tk.END)
    elif len(csv_files) > 0:
        messagebox.showinfo(
            "Search Completed", f"Search completed for {len(csv_files)} CSV file(s).\nTotal rows exported: {total_rows}")
        output_format_input.delete(0, tk.END)
    elif len(excel_files) > 0:
        messagebox.showinfo(
            "Search Completed", f"Search completed for {len(excel_files)} Excel file(s).\nTotal rows exported: {total_rows}")
        output_format_input.delete(0, tk.END)


def populate_column_options():
    cfg_filename = os.getcwd().replace('\\', '/') + '/new.cfg'
    folder_path = folder_entry.get()  # Get the selected folder path
    if folder_path:
        try:
            # Find all CSV and Excel files in the selected folder
            csv_files = [file for file in os.listdir(
                folder_path) if file.lower().endswith('.csv')]
            excel_files = [file for file in os.listdir(folder_path) if file.lower(
            ).endswith('.xls') or file.lower().endswith('.xlsx')]

            # Combine the lists of CSV and Excel files
            all_files = csv_files + excel_files

            if all_files:
                # Get the path of the first file
                file_path = os.path.join(folder_path, all_files[0])

                # Determine the file extension of the selected file
                file_extension = os.path.splitext(file_path)[1].lower()

                df = None  # Initialize df variable

                if file_extension == ".csv":
                    df = read_csv(file_path, encoding='utf-8',
                                  nrows=1, dtype=str)
                elif file_extension == ".xls" or file_extension == ".xlsx":
                    df = read_excel(file_path, nrows=1, dtype=str)

                if df is not None:
                    # Get the columns from the DataFrame's header
                    all_columns_list = df.columns.tolist()

                    # Set the first column as the default
                    column1_options.set(all_columns_list[0])
                    column2_options.set(all_columns_list[0])
                    column3_options.set(all_columns_list[0])
                    column4_options.set(all_columns_list[0])
                    column5_options.set(all_columns_list[0])
                    column6_options.set(all_columns_list[0])
                    column7_options.set(all_columns_list[0])
                    column8_options.set(all_columns_list[0])

                    column1_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column2_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column3_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column4_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column5_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column6_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column7_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options
                    column8_dropdown["menu"].delete(
                        0, tk.END)  # Clear the existing options

                    for column in all_columns_list:
                        column1_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column1_options, column))
                        column2_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column2_options, column))
                        column3_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column3_options, column))
                        column4_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column4_options, column))
                        column5_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column5_options, column))
                        column6_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column6_options, column))
                        column7_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column7_options, column))
                        column8_dropdown["menu"].add_command(
                            label=column, command=tk._setit(column8_options, column))

                    cfg_out = open(cfg_filename, 'w')
                    for column in all_columns_list:
                        cfg_out.write(str(column) + '\n')
                    cfg_out.close()

        except Exception as e:
            traceback.print_exc()  # Print the full stack trace of the exception
            messagebox.showerror(
                "Error", f"An error occurred while reading the file: {str(e)}")


# Create the GUI window
window = tk.Tk()
window.title("CSV Search and Export")
window.geometry("885x685")  # Adjust the window size

# Create an OptionMenu for logic selection
logic_var = tk.StringVar(window)
logic_var.set("AND")
logic_options = ["AND", "OR"]
logic_dropdown = tk.OptionMenu(window, logic_var, *logic_options)
logic_dropdown.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)


# Create the "Search" button and associate it with the execute_search function
search_button = tk.Button(window, text="Search", command=execute_search)

# Create and place the widgets using the grid layout manager
folder_label = tk.Label(window, text="Folder:")
folder_entry = tk.Entry(window, width=60)
browse_folder_button = tk.Button(window, text="Browse", command=browse_folder)


column_label = tk.Label(window, text="Column:")
column1_options = tk.StringVar(window)
column1_dropdown = tk.OptionMenu(window, column1_options, "")
column2_options = tk.StringVar(window)
column2_dropdown = tk.OptionMenu(window, column2_options, "")
column3_options = tk.StringVar(window)
column3_dropdown = tk.OptionMenu(window, column3_options, "")
column4_options = tk.StringVar(window)
column4_dropdown = tk.OptionMenu(window, column4_options, "")
column5_options = tk.StringVar(window)
column5_dropdown = tk.OptionMenu(window, column5_options, "")
column6_options = tk.StringVar(window)
column6_dropdown = tk.OptionMenu(window, column6_options, "")
column7_options = tk.StringVar(window)
column7_dropdown = tk.OptionMenu(window, column7_options, "")
column8_options = tk.StringVar(window)
column8_dropdown = tk.OptionMenu(window, column8_options, "")

output_format_label = tk.Label(window, text="Output format:")
output_format_options = tk.StringVar(window)
output_format_list = ['xlsx', 'csv']
output_format_options.set(output_format_list[0])
output_format_dropdown = tk.OptionMenu(
    window, output_format_options, *output_format_list)

search_label1 = tk.Label(window, text="Value 1:")
value1_entry = tk.Entry(window, width=60)

search_label2 = tk.Label(window, text="Value 2:")
value2_entry = tk.Entry(window, width=60)

search_label3 = tk.Label(window, text="Value 3:")
value3_entry = tk.Entry(window, width=60)

search_label4 = tk.Label(window, text="Value 4:")
value4_entry = tk.Entry(window, width=60)

search_label5 = tk.Label(window, text="Value 5:")
value5_entry = tk.Entry(window, width=60)

search_label6 = tk.Label(window, text="Value 6:")
value6_entry = tk.Entry(window, width=60)

search_label7 = tk.Label(window, text="Value 7:")
value7_entry = tk.Entry(window, width=60)

search_label8 = tk.Label(window, text="Value 8:")
value8_entry = tk.Entry(window, width=60)


search_type1_var = tk.StringVar(window)
search_type1_var.set("contains")
search_type1_dropdown = tk.OptionMenu(
    window, search_type1_var, "contains", "exact match")

search_type2_var = tk.StringVar(window)
search_type2_var.set("contains")
search_type2_dropdown = tk.OptionMenu(
    window, search_type2_var, "contains", "exact match")

search_type3_var = tk.StringVar(window)
search_type3_var.set("contains")
search_type3_dropdown = tk.OptionMenu(
    window, search_type3_var, "contains", "exact match")

search_type4_var = tk.StringVar(window)
search_type4_var.set("contains")
search_type4_dropdown = tk.OptionMenu(
    window, search_type4_var, "contains", "exact match")

search_type5_var = tk.StringVar(window)
search_type5_var.set("contains")
search_type5_dropdown = tk.OptionMenu(
    window, search_type5_var, "contains", "exact match")

search_type6_var = tk.StringVar(window)
search_type6_var.set("contains")
search_type6_dropdown = tk.OptionMenu(
    window, search_type6_var, "contains", "exact match")

search_type7_var = tk.StringVar(window)
search_type7_var.set("contains")
search_type7_dropdown = tk.OptionMenu(
    window, search_type7_var, "contains", "exact match")

search_type8_var = tk.StringVar(window)
search_type8_var.set("contains")
search_type8_dropdown = tk.OptionMenu(
    window, search_type8_var, "contains", "exact match")


# Place the widgets using the grid layout manager
folder_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
folder_entry.grid(row=0, column=1, columnspan=3,
                  padx=5, pady=5, sticky=tk.W + tk.E)
browse_folder_button.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)


column_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
column1_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label1.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
value1_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column2_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label2.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
value2_entry.grid(row=3, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column3_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label3.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
value3_entry.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column4_dropdown.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label4.grid(row=5, column=2, padx=5, pady=5, sticky=tk.W)
value4_entry.grid(row=5, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column5_dropdown.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label5.grid(row=6, column=2, padx=5, pady=5, sticky=tk.W)
value5_entry.grid(row=6, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column6_dropdown.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label6.grid(row=7, column=2, padx=5, pady=5, sticky=tk.W)
value6_entry.grid(row=7, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column7_dropdown.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label7.grid(row=8, column=2, padx=5, pady=5, sticky=tk.W)
value7_entry.grid(row=8, column=3, padx=5, pady=5, sticky=tk.W + tk.E)

column8_dropdown.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W + tk.E)
search_label8.grid(row=9, column=2, padx=5, pady=5, sticky=tk.W)
value8_entry.grid(row=9, column=3, padx=5, pady=5, sticky=tk.W + tk.E)


search_type1_dropdown.grid(row=2, column=4, padx=5, pady=5, sticky=tk.W)
search_type2_dropdown.grid(row=3, column=4, padx=5, pady=5, sticky=tk.W)
search_type3_dropdown.grid(row=4, column=4, padx=5, pady=5, sticky=tk.W)
search_type4_dropdown.grid(row=5, column=4, padx=5, pady=5, sticky=tk.W)
search_type5_dropdown.grid(row=6, column=4, padx=5, pady=5, sticky=tk.W)
search_type6_dropdown.grid(row=7, column=4, padx=5, pady=5, sticky=tk.W)
search_type7_dropdown.grid(row=8, column=4, padx=5, pady=5, sticky=tk.W)
search_type8_dropdown.grid(row=9, column=4, padx=5, pady=5, sticky=tk.W)


output_format_label.grid(row=10, column=0, padx=5, pady=5, sticky=tk.W)
output_format_dropdown.grid(row=10, column=1, padx=5, pady=5, sticky=tk.W)

# Create and place the input field for output format
output_filename_prefix = tk.Label(window, text="Output filename prefix: ")
output_format_input = tk.Entry(window)
output_format_input.grid(row=10, column=3, padx=5, pady=5, sticky=tk.W + tk.E)
output_filename_prefix.grid(row=10, column=2, padx=5, pady=5, sticky=tk.W)

search_button.grid(row=11, column=0, columnspan=5,
                   padx=5, pady=5, sticky=tk.W + tk.E)


error_text = tk.Text(window, height=10, width=80)
error_text.grid(row=12, column=0, columnspan=5, padx=5, pady=5)


def log_error(error_message):
    search_errors.append(error_message)
    error_text.insert(tk.END, error_message + "\n")
    error_text.see(tk.END)  # Scroll to the end of the text


folder_entry.bind("<FocusOut>", lambda event: populate_column_options())


def main():
    try:
        # Start the GUI event loop
        window.mainloop()

    except Exception as e:
        traceback.print_exc()  # Print the full stack trace of the exception
        print(traceback.format_exc())  # Print error to console


if __name__ == "__main__":
    main()
