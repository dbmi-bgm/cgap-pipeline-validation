import json
import pandas as pd

def generate_values(df, no_gparents, gparents):
    ngrandparents_list = []
    grandparents_list = []
    percentage_ngrandparents_list = []
    percentage_grandparents_list = []

    #iterate through each sample in dataframe and append values
    for sample in list(df['sample']):
        temp_ngrandparents = []
        temp_grandparents = []

        percentage_ngrandparent = ['', '', '']
        percentage_grandparent = ['', '', '']

        #get current index of the sample in the dataframe
        index = list(df['sample']).index(sample)

        #append individual sample name into each list
        temp_ngrandparents.append(int(sample[sample.index('I')+3:sample.index('_')]))
        temp_grandparents.append(int(sample[sample.index('I')+3:sample.index('_')]))

        ngrandparent_value_list = list(no_gparents.loc[index].values)
        grandparent_value_list = list(gparents.loc[index].values)

        #append total value for each parent into list i.e. total in parents (=not in grandparents + grandparents)
        total = sum(ngrandparent_value_list) + sum(grandparent_value_list)
        temp_ngrandparents.append(total)
        temp_grandparents.append(total)

        #append not in grandparents/in grandparents total value
        temp_ngrandparents.append(sum(ngrandparent_value_list))
        temp_grandparents.append(sum(grandparent_value_list))

        #append value of variant in each sibling
        temp_ngrandparents.extend(ngrandparent_value_list)
        temp_grandparents.extend(grandparent_value_list)

        #calculate percentage for each individual
        percentage_ngrandparent.extend([0.00 if value == 0 else value/total for value in ngrandparent_value_list])
        percentage_grandparent.extend([0.00 if value == 0 else value/total for value in grandparent_value_list])

        ngrandparents_list.append(temp_ngrandparents)
        grandparents_list.append(temp_grandparents)

        percentage_ngrandparents_list.append(percentage_ngrandparent)
        percentage_grandparents_list.append(percentage_grandparent)

    average_ngp = [(x+y)/2 if x!='' and y!='' else '' for x,y in zip(*percentage_ngrandparents_list)]
    average_gp = [(x+y)/2 if x!='' and y!='' else '' for x,y in zip(*percentage_grandparents_list)]

    ngrandparents_list.extend(percentage_ngrandparents_list)
    ngrandparents_list.append(average_ngp)

    grandparents_list.extend(percentage_grandparents_list)
    grandparents_list.append(average_gp)

    return ngrandparents_list, grandparents_list

def generate_columns(df):
    max_number = 0
    for column in df.columns:
        if 'by_siblings' in column:
            column = column[len('by_siblings')+1:]
            column = column[:column.index('.')]
            if int(column) > max_number:
                max_number = int(column)

    multindex_ng_tuple = [('','sample_name'),('','total in parents'), ('', 'not in grandparents')] + [('in siblings', int(i))for i in range(0, max_number+1)]
    multindex_g_tuple = [('','sample_name'),('','total in parents'), ('', 'in grandparents')] + [('in siblings', int(i))for i in range(0, max_number+1)]
    ng_df_index = pd.MultiIndex.from_tuples(multindex_ng_tuple)
    g_df_index = pd.MultiIndex.from_tuples(multindex_g_tuple)
    return ng_df_index, g_df_index

def write_to_excel(dataframe_list, file_name, sheet_name):
    row = 0
    writer = pd.ExcelWriter(file_name + '.xlsx')

    for dataframe in dataframe_list:
        dataframe.to_excel(writer, sheet_name, startrow=row)
        #hide the extra row generated
        writer.sheets[sheet_name].set_row(2 + row, None, None, {'hidden': True})
        #add name for the first column as it will be hidden
        bold   = writer.book.add_format({'bold': True, 'align': 'center'})
        writer.sheets[sheet_name].write(1 + row, 0, 'sample_name', bold)

        #add percentage formatting for the last three rows of the dataframe
        percentage = writer.book.add_format({'num_format': '0.00%'})
        writer.sheets[sheet_name].set_row(5 + row, None, percentage)
        writer.sheets[sheet_name].set_row(6 + row, None, percentage)
        writer.sheets[sheet_name].set_row(7 + row, None, percentage)
        writer.sheets[sheet_name].write(7 + row, 2, 'Average', bold)

        #iterate through
        for idx, column in enumerate(dataframe.columns):
            if idx == 0:
                writer.sheets[sheet_name].set_column(idx, idx, len(max(list(column))) + 2)
            # adjusts column width
            if 'in siblings' not in list(column):
                column_length = len(max(list(column))) + 2
            else:
                #set the column width as in sibling length if already present in the column
                column_length = len('in siblings')
            writer.sheets[sheet_name].set_column(idx + 2, idx + 1, column_length)

        #adjust length for the row to write the next dataframe within list
        row = row + len(dataframe.index) + dataframe.columns.nlevels + 3

    writer.save()

def main():
    # input file name separated by space
    file_name = input("Enter file name(s): ")
    if file_name == '':
        file_name = '/Users/catherinesong/Documents/2022/Park_Lab/granite_het_filter/GAPFIEK1LK1A.het.snv.json'
    excel_name = input("Enter excel file name: ")
    #file /Users/catherinesong/Documents/2022/Park_Lab/granite_het_filter/GAPFIEK1LK1A.het.snv.json

    #/Users/catherinesong/Downloads/Untitled.txt
    file = open(file_name, "r")
    fileData = file.read()
    jsonData = json.loads(fileData)
    df = pd.json_normalize(jsonData["autosomal heterozygous calls error, GENERAL"])

    #get the number of variants not in grandparents for filtered and non-filtered values
    no_gparents_df = df.loc[:,df.columns.str.contains("no_spouse.no_gparents")]
    no_gparents_filtered_df = df.loc[:,df.columns.str.contains("no_spouse.is_ID.no_gparents")]

    #get the number of variants in grandparents for filtered and non-filtered values
    gparents_df = df.loc[:,df.columns.str.contains("no_spouse.in_gparents")]
    gparents_filtered_df = df.loc[:,df.columns.str.contains("no_spouse.is_ID.in_gparents")]

    #generate columns for filtered and non-filtered dataframe
    ng_index, g_index = generate_columns(df)

    #generate values for filtered and nonfiltered values
    notgp_value, gp_value =  generate_values(df, no_gparents_df, gparents_df)
    notgp_filtered_value, gp_filtered_value = generate_values(df, no_gparents_filtered_df, gparents_filtered_df)

    #non_filtered values
    ng_df = pd.DataFrame(notgp_value, columns = ng_index)
    ng_df = ng_df.set_index(ng_df.columns[0])

    g_df = pd.DataFrame(gp_value, columns = g_index)
    g_df = g_df.set_index(g_df.columns[0])
    non_filtered_df = [ng_df, g_df]

    #filtered values
    ng_filtered_df = pd.DataFrame(notgp_filtered_value, columns = ng_index)
    ng_filtered_df = ng_filtered_df.set_index(ng_filtered_df.columns[0])

    g_filtered_df = pd.DataFrame(gp_filtered_value, columns = g_index)
    g_filtered_df = g_filtered_df.set_index(g_filtered_df.columns[0])
    filtered_df = [ng_filtered_df, g_filtered_df]

    write_to_excel(non_filtered_df, excel_name + '_het_all_variants', 'all variants')
    write_to_excel(filtered_df, excel_name + 'het_known_variants', 'known variants')

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(ng_df)

main()