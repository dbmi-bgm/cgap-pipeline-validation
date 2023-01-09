# cgap-pipeline-validation

This repository is used to generate accession and trio files used to upload families into the CGAP pipeline.

``` trio_output.py ``` takes in an input file and family ID number and will generate a set of trios for all possible parent-offspring combination in the family (including parent-offspring trio and grandparent-parent trios). The python script will output a set of trios excel files for each offspring and their parents.

```accession_pedigree_file_generation.py``` takes in an input file, family ID number, proband ID and will generate an accessioning file and pedigree file for the selected family. The accessioning file contains information including the unique_analysis_id, family_id, analysis_id, file locations and so on for the family while the pedigree contains information that is related to the characteristics of each individual within the family including hpo_terms, mondo_terms and so on.

```granite_het_automation.py``` will automate the results from ```./het_stat.sh``` or ```./het_indel_snv.sh```

Example Code:

python3 granite_het_automation.py GAPFII5YI4XJ.het.indel.json (json output) family_22_indel (file output name)


```granite_denovo_automation.py``` will automate the results from ```./denovo_stat.sh```

Example Code:

python3 granite_denovo_automation.py GAPETMPGNUOI.novo.indel.ison (json output) family_22_children.csv (csv file with matching individual and corresponding file name) family_22_children_denovo y (indicating that children file is being read, n for parents)
