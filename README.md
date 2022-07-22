# cgap-pipeline-validation

This repository is used to generate accession and trio files used to upload families into the CGAP pipeline.

``` trio_output.py ``` takes in an input file and family ID number and will generate a set of trios for all possible parent-offspring combination in the family (including parent-offspring trio and grandparent-parent trios). The python script will output a set of trios excel files for each offspring and their parents.

```accession_pedigree_file_generation.py``` takes in an input file, family ID number, proband ID and will generate an accessioning file and pedigree file for the selected family. The accessioning file contains information including the unique_analysis_id, family_id, analysis_id, file locations and so on for the family while the pedigree contains information that is related to the characteristics of each individual within the family including hpo_terms, mondo_terms and so on.
