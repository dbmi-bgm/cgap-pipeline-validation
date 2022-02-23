import pandas
import numpy as np
from pandas import DataFrame


def generate_accession_individual(family_id, df, proband_status, gender='U', report_required='No'):
    # check if mother and father dataframes are empty before assigning their Ids
    subject_id = 'IND' + str(df.Subject)
    analysis_id = family_id
    unique_analysis_id = family_id + '_' + subject_id

    individual_id_UGRP = 'UGRP' + subject_id
    sample_id = individual_id_UGRP + '_sample'

    if proband_status is 'Proband':
        report_required = 'Yes'
    else:
        report_required = 'No'

    return [unique_analysis_id, family_id, analysis_id, individual_id_UGRP, proband_status, 'Peripheral Blood',
            sample_id, gender, report_required, 'WGS', '']


# read file input from commandline
file_name = input("Enter file name: ")
file_name = file_name.strip()
if file_name == "":
    family_df = pandas.read_excel("_fam_sub_mot_fat_sam_sex_con_con_con_use_sra_twn.xlsx")

else:
    family_df = pandas.read_excel(file_name)

# read family number input from commandline
input_string = input("Enter family ID: ")
input_string = input_string.strip()

# if no input is provided then use the default input of family 10
if input_string == "":
    # family_list_of_interest = [10, 11, 22, 23, 25, 28, 33]
    family_number = 'UGRP' + '10'
    input_string = 10
# else read the user input
elif input_string.isnumeric():
    # family_list = input_string.split(" ")
    # family_list = [int(i) for i in family_list]
    family_number = 'UGRP' + input_string

# extract the matching family
temp = family_df.loc[family_df['Family'] == int(input_string)]
# drop the hidden columns
temp = temp.drop(columns=['Mother', 'Father', 'Sample', 'Sex', 'Run'])
# rename columns for mother and father
temp = temp.rename({'Mother.1': 'Mother', 'Father.1': 'Father'}, axis='columns')

# extract children
child_df = temp.loc[pandas.notna(temp['Child'])]
# extract mother
mother_df = temp.loc[pandas.notna(temp['Mother'])]
# extract father
father_df = temp.loc[pandas.notna(temp['Father'])]
# extract maternal grandparents
maternal_df = temp.loc[pandas.notna(temp['Maternal Grandparent'])]
# extract paternal grandparents
paternal_df = temp.loc[pandas.notna(temp['Paternal Grandparent'])]

proband_number = input("Enter proband ID: ")
if proband_number == "" or proband_number not in child_df.Subject:
    # specify first child as proband if no proband number is chosen or the proband is not found in the children df
    proband_number = child_df.Subject.iloc[0]

accession_file_df = pandas.DataFrame()
accession_file_list = []

for i in range(len(child_df)):
    if child_df.iloc[i].Subject == proband_number:
        accession_file_list.append(generate_accession_individual(family_number, child_df.iloc[i],
                                                                 'Proband', child_df.iloc[i].Child, 'Yes'))
    else:
        accession_file_list.append(generate_accession_individual(family_number, child_df.iloc[i],
                                                                 'Sibling', child_df.iloc[i].Child))

accession_file_list.append(generate_accession_individual(family_number, mother_df.iloc[0],
                                                         'Mother', mother_df.iloc[0].Mother))

accession_file_list.append(generate_accession_individual(family_number, father_df.iloc[0],
                                                         'Father', father_df.iloc[0].Father))

for i in range(len(maternal_df)):
    if maternal_df.iloc[i]['Maternal Grandparent'] is 'F':
        accession_file_list.append(generate_accession_individual(family_number, maternal_df.iloc[i],
                                                                 'Maternal Grandmother',
                                                                 maternal_df.iloc[i]['Maternal Grandparent']))
    else:
        accession_file_list.append(generate_accession_individual(family_number, maternal_df.iloc[i],
                                                                 'Maternal Grandfather',
                                                                 maternal_df.iloc[i]['Maternal Grandparent']))

for i in range(len(paternal_df)):
    if paternal_df.iloc[i]['Paternal Grandparent'] is 'F':
        accession_file_list.append(generate_accession_individual(family_number, paternal_df.iloc[i],
                                                                 'Paternal Grandmother',
                                                                 paternal_df.iloc[i]['Paternal Grandparent']))
    else:
        accession_file_list.append(generate_accession_individual(family_number, paternal_df.iloc[i],
                                                                 'Paternal Grandfather',
                                                                 paternal_df.iloc[i]['Paternal Grandparent']))


accession_file_df = pandas.DataFrame(accession_file_list,
                                     columns=['Unique Analysis ID:', 'Family ID:', 'Analysis ID:', 'Individual ID:',
                                              'Relation to Proband:', 'Specimen Type:', 'Specimen ID:', 'Sex:',
                                              'Report Required', 'Test Requested:', 'Files:'])

# generate a writer for excel formatting
writer = pandas.ExcelWriter(family_number + "_accession_file.xlsx", engine='xlsxwriter')
accession_file_df.to_excel(writer, sheet_name='Sheet1', startrow=1, index=False, header=False)
workbook = writer.book
worksheet = writer.sheets['Sheet1']

# modify the headers and set the column width to 30
header_format = workbook.add_format({'bold': False, 'valign': 'left'})
for col_num, value in enumerate(accession_file_df.columns.values):
    worksheet.write(0, col_num, value, header_format)
    worksheet.set_column(0, col_num, 30)
writer.save()