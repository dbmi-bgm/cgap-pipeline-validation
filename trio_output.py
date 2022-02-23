import pandas
import numpy as np
from pandas import DataFrame


def generate_family_list(family_id, df, mother_dataframe, father_dataframe, gender='U'):
    temp_family_list = []
    proband_individuals = []
    # check if mother and father dataframes are empty before assigning their Ids
    if not mother_dataframe.empty:
        mother_id = 'IND' + str(mother_dataframe.iloc[0]['Subject'])
    else:
        mother_id = ''
    if not father_dataframe.empty:
        father_id = 'IND' + str(father_dataframe.iloc[0]['Subject'])
    else:
        father_id = ''

    # iterate through all the offspring
    for i in range(len(df)):
        # generate individual id
        subject_id = 'IND' + str(df.iloc[i]['Subject'])

        # other terms for the pedigree spreadsheet
        hpo_term = ''
        mondo_terms = ''
        proband = 'N'
        clinical_notes = ''
        ancestry = ''
        life_status = ''
        deceased = ''
        cause_of_death = ''
        age_of_death = ''
        age_at_death_units = ''
        pregnancy = ''
        gestational_age = ''
        gestational_age_units = ''
        pregnancy_termination = ''
        spontangeous_abortion = ''
        still_birth = ''
        no_children_by_choice = ''
        infertile = ''
        cause_of_infertility = ''
        quantity = ''

        # generate the trio before appending it to the family list
        # only generate the trio if there exists both a father and mother for the child
        if not mother_dataframe.empty and not father_dataframe.empty:
            generate_trio(family_id, subject_id, mother_id, father_id, gender)
            proband_individuals.append('UGRP' + subject_id)

        # add UGRP for individuals to be used in the pedigree excel sheet
        if mother_id is not '':
            ugrp_mother_id = 'UGRP' + mother_id
        else:
            ugrp_mother_id = ''

        if father_id is not '':
            ugrp_father_id = 'UGRP' + father_id
        else:
            ugrp_father_id = ''

        ugrp_subject_id = 'UGRP' + subject_id

        # append offspring to the family list
        temp_family_list.append(
            [family_id, ugrp_subject_id, gender, ugrp_mother_id, ugrp_father_id, hpo_term, mondo_terms, proband,
             clinical_notes, ancestry, life_status, deceased, cause_of_death, age_of_death,
             age_at_death_units, pregnancy, gestational_age, gestational_age_units,
             pregnancy_termination,
             spontangeous_abortion, still_birth, no_children_by_choice, infertile,
             cause_of_infertility,
             quantity])

    return temp_family_list, proband_individuals


def generate_trio(family_id, individual_id, mother_id, father_id, gender):
    # generate analysis ID for trio
    analysis_id = family_id + '_' + mother_id + '_' + father_id + '_' + individual_id

    # add UGRP onto id names to be used for individual_id and sample_id
    individual_id_UGRP = 'UGRP' + individual_id
    mother_id_UGRP = 'UGRP' + mother_id
    father_id_UGRP = 'UGRP' + father_id
    trio_list = []

    for i in range(3):
        # set values depending on the iteration for proband, and father and mother
        # the order will always be proband -> mother -> father in the trio
        if i == 0:
            proband = 'Proband'
            unique_analysis_id = family_id + '_' + individual_id + '_' + mother_id + '_' + father_id
            sample_id = individual_id_UGRP + '_sample'
            report_required = 'Yes'
            trio_list.append(
                [unique_analysis_id, family_id, analysis_id, individual_id_UGRP, proband, 'Peripheral Blood',
                 sample_id, gender, report_required, 'WGS', ''])

        elif i == 1:
            proband = 'Mother'
            unique_analysis_id = family_id + '_' + mother_id + '_' + individual_id + '_' + father_id
            sample_id = mother_id_UGRP + '_sample'
            report_required = 'No'
            trio_list.append([unique_analysis_id, family_id, analysis_id, mother_id_UGRP, proband, 'Peripheral Blood',
                              sample_id, 'F', report_required, 'WGS', ''])

        else:
            proband = 'Father'
            unique_analysis_id = family_id + '_' + father_id + '_' + individual_id + '_' + mother_id
            sample_id = father_id_UGRP + '_sample'
            report_required = 'No'
            trio_list.append([unique_analysis_id, family_id, analysis_id, father_id_UGRP, proband, 'Peripheral Blood',
                              sample_id, 'M', report_required, 'WGS', ''])

    # generate trio dataframe to be outputted to Excel
    trio_df = pandas.DataFrame(trio_list,
                               columns=['Unique Analysis ID:', 'Family ID:', 'Analysis ID:', 'Individual ID:',
                                        'Relation to Proband:', 'Specimen Type:', 'Specimen ID:', 'Sex:',
                                        'Report Required', 'Test Requested:', 'Files:'])

    # generate a writer for excel formatting
    writer = pandas.ExcelWriter(analysis_id + ".xlsx", engine='xlsxwriter')
    trio_df.to_excel(writer, sheet_name='Sheet1', startrow=1, index=False, header=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # modify the headers and set the column width to 30
    header_format = workbook.add_format({'bold': False, 'valign': 'left'})
    for col_num, value in enumerate(trio_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, col_num, 30)
    writer.save()


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
    # family_list = [10, 11, 22, 23, 25, 28, 33]
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

family_df = pandas.DataFrame()
family_df_list = []
proband_list = []

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

# append children to dataframe list
family_temp_list, proband_temp_list = generate_family_list(family_number, child_df, mother_df, father_df)
family_df_list.extend(family_temp_list)
proband_list.extend(proband_temp_list)

# append mother to dataframe list
if ('F' in mother_df.Mother.item()):
    family_temp_list, proband_temp_list = generate_family_list(family_number, mother_df,
                                                               maternal_df.loc[
                                                                   maternal_df['Maternal Grandparent'] == 'F'],
                                                               maternal_df.loc[
                                                                   maternal_df['Maternal Grandparent'] == 'M'],
                                                               mother_df.Mother.item())

    family_df_list.extend(family_temp_list)
    proband_list.extend(proband_temp_list)

# append father to dataframe list
if ('M' in father_df.Father.item()):
    family_temp_list, proband_temp_list = generate_family_list(family_number, father_df,
                                                               paternal_df.loc[
                                                                   paternal_df['Paternal Grandparent'] == 'F'],
                                                               paternal_df.loc[
                                                                   paternal_df['Paternal Grandparent'] == 'M'],
                                                               father_df.Father.item())

    family_df_list.extend(family_temp_list)
    proband_list.extend(proband_temp_list)

# append paternal grandfather to dataframe list
if ('M' in paternal_df['Paternal Grandparent'].values.tolist()):
    family_temp_list, _ = generate_family_list(family_number,
                                               paternal_df.loc[paternal_df['Paternal Grandparent'] == 'M'],
                                               pandas.DataFrame, pandas.DataFrame,
                                               paternal_df.loc[paternal_df['Paternal Grandparent'] == 'M'][
                                                   'Paternal Grandparent'].item())

    family_df_list.extend(family_temp_list)

# append paternal grandmother to dataframe list
if ('F' in paternal_df['Paternal Grandparent'].values.tolist()):
    family_temp_list, _ = generate_family_list(family_number,
                                               paternal_df.loc[paternal_df['Paternal Grandparent'] == 'F'],
                                               pandas.DataFrame, pandas.DataFrame,
                                               paternal_df.loc[paternal_df['Paternal Grandparent'] == 'F'][
                                                   'Paternal Grandparent'].item())
    family_df_list.extend(family_temp_list)

# append maternal grandfather to dataframe list
if ('M' in maternal_df['Maternal Grandparent'].values.tolist()):
    family_temp_list, _ = generate_family_list(family_number,
                                               maternal_df.loc[maternal_df['Maternal Grandparent'] == 'M'],
                                               pandas.DataFrame,
                                               pandas.DataFrame,
                                               maternal_df.loc[maternal_df['Maternal Grandparent'] == 'M'][
                                                   'Maternal Grandparent'].item())
    family_df_list.extend(family_temp_list)

# append maternal grandmother to dataframe list
if ('F' in maternal_df['Maternal Grandparent'].values.tolist()):
    family_temp_list, _ = generate_family_list(family_number,
                                               maternal_df.loc[maternal_df['Maternal Grandparent'] == 'F'],
                                               pandas.DataFrame,
                                               pandas.DataFrame,
                                               maternal_df.loc[maternal_df['Maternal Grandparent'] == 'F'][
                                                   'Maternal Grandparent'].item())
    family_df_list.extend(family_temp_list)

# generate pedigree
pedigree_df: DataFrame = pandas.DataFrame(family_df_list,
                                          columns=['Family ID', 'Individual ID', 'Sex',
                                                   'Mother ID', 'Father ID', 'HPO terms', 'MONDO terms',
                                                   'Proband', 'Clinical Notes', 'Ancestry', 'Life Status', 'Deceased',
                                                   'Cause of death',
                                                   'Age at death', 'Age at death units', 'Pregnancy', 'Gestational age',
                                                   'Gestational age units', 'Is termination of pregnancy',
                                                   'Spontaneous abortion',
                                                   'Still birth', 'No children by choice', 'Infertile',
                                                   'Cause of infertility',
                                                   'Quantity'])

# generate a writer for excel formatting
for individual in proband_list:
    writer = pandas.ExcelWriter(family_number + '_pedigree_' + individual + ".xlsx", engine='xlsxwriter')
    # modify for the individual as the proband
    pedigree_df.loc[pedigree_df["Individual ID"] == individual, "Proband"] = "Y"
    pedigree_df.to_excel(writer, sheet_name='Sheet1', startrow=1, index=False, header=False)
    # convert the proband back to 'N' after writing to excel
    pedigree_df.loc[pedigree_df["Individual ID"] == individual, "Proband"] = "N"

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # modify the headers and set the column width to 30
    header_format = workbook.add_format({'bold': False, 'valign': 'left'})
    for col_num, value in enumerate(pedigree_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, col_num, 15)
    writer.save()


# generate general pedigree for whole family where all individuals are not proband
    writer = pandas.ExcelWriter(family_number + '_pedigree_' +  ".xlsx", engine='xlsxwriter')
    pedigree_df.to_excel(writer, sheet_name='Sheet1', startrow=1, index=False, header=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # modify the headers and set the column width to 30
    header_format = workbook.add_format({'bold': False, 'valign': 'left'})
    for col_num, value in enumerate(pedigree_df.columns.values):
        worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, col_num, 15)
    writer.save()

