import os
import sys

import pandas as pd
import numpy as np
from numpy import cumsum
import json
import re
from xlsxwriter import Workbook


def read_file(filename):
    file = open(filename, "r")
    fileData = file.read()
    jsonData = json.loads(fileData)

    # need condition if file name is .snv then we want to read de novo error calls etc.
    novo_df = pd.json_normalize(jsonData['de novo calls error']).T
    return novo_df


def store_values(novo_df):
    novo_list_1 = []
    novo_list_2 = []
    novo_list_3 = []
    # iterate through each column of the dataframe
    for key in novo_df.index:
        # store the corresponding list based column value
        value_list = novo_df.loc[key].tolist()
        for i in range(len(value_list)):
            if i == 1:
                novo_list_1.append(value_list[i])
            elif i == 2:
                novo_list_2.append(value_list[i])
            else:
                novo_list_3.append(value_list[i])
    return novo_list_1, novo_list_2, novo_list_3


def multi_level_index(novo_df, novo_pp_values):
    column_tuple_1 = []
    column_tuple_2 = []
    column_tuple_3 = []
    # create tuples for the multi-level index
    for key in novo_df.index:
        if ", " not in key:
            for i in range(len(novo_pp_values)):
                if i == 1:
                    column_tuple_1.append(["novoPP" + novo_pp_values[i], '', key])
                elif i == 2:
                    column_tuple_2.append(["novoPP" + novo_pp_values[i], '', key])
                else:
                    column_tuple_3.append(["novoPP" + novo_pp_values[i], '', key])

        # split the key into two values for not in grandparents, in siblings etc.
        else:
            split_key = key.split(",")
            for i in range(len(novo_pp_values)):
                temp_key = ["novoPP" + novo_pp_values[i]] + split_key
                if i == 1:
                    column_tuple_1.append(temp_key)
                elif i == 2:
                    column_tuple_2.append(temp_key)
                else:
                    column_tuple_3.append(temp_key)

    return column_tuple_1, column_tuple_2, column_tuple_3


def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]


def calculate_percentage(df):
    #calculates the percentage for each of the individual
    percentage_index = pd.MultiIndex.from_tuples([('', '')]* 4 + df.columns.to_list()[4: ])
    percentage_df = pd.DataFrame(columns=percentage_index)

    for index in df.index:
        if index != 'Sum':
            total = df.loc[index].values[2]
            sum_values = cumsum(df.loc[index].values[4:])
            if total == 0.0:
                #if there was no value recorded for a particular level then assign 1.0 to avoid undefined values
                percentage = [str(100.0) + '%']*len(sum_values)
            else:
                #calculate the expected values
                percentage = (sum_values/total)
                #round to 2dp
                percentage = [str(round(values * 100, 2)) + '%' for values in percentage]
            percentage_df.loc[index] = [''] * 4 + percentage
    return percentage_df

def write_to_excel(dataframe_list, name, row_to_hide=3):
    # create a full excel_spread sheet to check for errors
    writer = pd.ExcelWriter(name + '.xlsx')

    #iterate through dataframe list
    row = 0
    for dataframe in dataframe_list:
        dataframe.to_excel(writer, 'Sheet 1', startrow = row)
        #loop through each column
        for idx, column in enumerate(dataframe.columns):
            #adjust the length for the first column based on its values i.e. individual file names
            if column!=('',''):
                if idx == 0:
                    writer.sheets['Sheet 1'].set_column(idx, idx, len(max(dataframe.index.to_list(), key=len)) + 2)
                # adjusts column width
                column_length = len(max(list(column))) + 2
                writer.sheets['Sheet 1'].set_column(idx + 2, idx + 1, column_length)

        column_length = len(max(list(column)))
        # need to adjust column width for the last column
        writer.sheets['Sheet 1'].set_column(len(dataframe.columns), len(dataframe.columns), column_length)
        # remove random empty line generated by excel writer
        writer.sheets['Sheet 1'].set_row(row_to_hide + row, None, None, {'hidden': True})

        # we need to account for multilevel columns and the rows so that there is space between the two dataframes
        row = row + len(dataframe.index) + dataframe.columns.nlevels + 3

    writer.save()


def main():
    # input file name separated by space
    input("To use the script would need the json file name from denovo granite analysis, an "
          "excel file containing column of individual ID number, file name for the individual and their "
          "corresponding roles in the family. An excel name for the outputted excel and whether if they are "
          "children files. \n Press enter to continue\n")
    commandline_input = sys.argv
    file_name = commandline_input[1:len(commandline_input)-3]
    family_name = commandline_input[len(commandline_input)-3]
    excel_name = commandline_input[len(commandline_input)-2]
    is_children = commandline_input[len(commandline_input)-1]

    if is_children.lower() == 'y':
        is_children= True
    elif is_children.lower() =='n' or is_children.lower()=='':
        is_children = False
    else:
        print("Wrong input please input Y/N" ,sys.stderr)
        sys.exit()

    # only read parent or children and not both together
    if file_name == "":
        file_name = ["/Users/catherinesong/Documents/2022/Park_Lab/Family_10/denovo/parents/GAPFI931UKDP.novo.snv.json",
                     "/Users/catherinesong/Documents/2022/Park_Lab/Family_10/denovo/parents/GAPFIHVJRQXF.novo.snv.json"]
    else:
        file_name = file_name

    if family_name == "":
        family_file = pd.read_csv(
            "/Users/catherinesong/Documents/2022/Park_Lab/Family_10/denovo/Family_10_parent_ID.csv")
    else:
        if os.path.exists(family_name):
            family_file = pd.read_csv(family_name)
        else:
            print("No such family file '{}' exists!".format(family_name), file=sys.stderr)
            sys.exit()

    excel_df = pd.DataFrame()

    # for the input file name iterate through each file
    for file in file_name:
        # read the file into a dataframe
        if os.path.exists(file):
            novo_df = read_file(file)
        else:
            print("No such json file '{}' exists!".format(file), file=sys.stderr)
            sys.exit()

        novo_pp_values = novo_df.loc['novoPP']
        novo_df = novo_df.drop(index=('novoPP'))

        # generate number of lists based on the available novo_pp_values
        novo_value_list_1, novo_value_list_2, novo_value_list_3 = store_values(novo_df)
        # create multilevel index values
        column_tuple_list_1, column_tuple_list_2, column_tuple_list_3 = multi_level_index(novo_df, novo_pp_values)

        # create multi-level index
        excel_column = pd.MultiIndex.from_tuples(column_tuple_list_1 + column_tuple_list_2 + column_tuple_list_3)

        # rename the column as required
        column_name = file[:file.find('.')]
        if '/' in column_name:
            # removes the file path of the string and only keeps the name
            column_name = column_name.rsplit('/', 1)[-1]
        # store each entry into temp dataframe
        temp_df = pd.DataFrame((novo_value_list_1 + novo_value_list_2 + novo_value_list_3), index=excel_column,
                               columns=[column_name])
        # dropNA values
        temp_df = temp_df[temp_df[column_name].notna()]
        # append to final excel_df
        excel_df = excel_df.append(temp_df.T, sort=False)

    # iterate through each novoPP value and split into three separate excel files
    unique_level = set(excel_df.columns.get_level_values(0))
    for level in unique_level:
        temp_df = excel_df.iloc[:, excel_df.columns.get_level_values(0).str.contains(level)]

        # drop top level as it will now be our file name
        temp_df.columns = temp_df.columns.droplevel()

        # change ordering for level 2
        column_list = temp_df.columns.get_level_values(1)
        # find where the digit first appears

        level_0 = list(temp_df.columns.get_level_values(0))
        if len([idx for idx, s in enumerate(column_list) if re.search(r"\d+", s)]) > 1:
            print(len([idx for idx, s in enumerate(column_list) if re.search(r"\d+", s)]))
        digit_index = [idx for idx, s in enumerate(column_list) if re.search(r"\d+", s)][0]
        # sort the string columns first
        string_columns = list(column_list[:digit_index])
        string_columns.sort(reverse=True)
        # sort non-string columns
        digit_columns = list(column_list[digit_index:])
        digit_columns.sort(key=num_sort)

        # getting the level 1 and level 0 columns
        level_1 = string_columns + digit_columns

        # create a new ordered column
        new_column_tuple = [(level_0[i], level_1[i]) for i in range(0, len(level_0))]
        multi_cols = pd.MultiIndex.from_tuples(new_column_tuple)
        temp_df = pd.DataFrame(temp_df, columns=multi_cols)

        # insert individual ID into the temporary dataframe
        identifier = [family_file.loc[family_file['File_ID'] == i].Individual_ID.values.item() for i in
                      temp_df.index.tolist()]

        # find the role of the individual within the family file
        role = [family_file.loc[family_file['File_ID'] == i].Individual.values.item() for i in temp_df.index.tolist()]
        # store the individual identifier and their role into the dataframe
        temp_df['', 'individual_ID'] = identifier
        temp_df['', 'role'] = role

        # reorder the column order
        temp_cols = temp_df.columns.tolist()
        new_cols = temp_cols[-2:] + temp_cols[0:-2]
        temp_df = temp_df[new_cols]

        # add sum row to the temp_df
        temp_df.loc['Sum'] = [None] * (len(temp_df.columns))
        temp_df.iloc[:, 2:] = temp_df.iloc[:, 2:].fillna(0)
        for column in temp_df.columns[2:]:
            temp_df.at['Sum', column] = temp_df[column].sum()

        #calculate the percentages for the children and write to file
        if is_children:
            percentage_df = calculate_percentage(temp_df)

            # write to excel with specified name
            write_to_excel([temp_df, percentage_df], level + '_' + excel_name, 2)

        #write to file for parents
        else:
            write_to_excel([temp_df], level + '_' + excel_name, 2)


main()
