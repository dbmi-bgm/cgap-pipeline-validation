import os
import subprocess
import sys

if len(sys.argv) < 2:
    print("Please provide a vcf file to proceed; The format should be python mutation_type.py xxx.vcf.gz xxx.vcf.gz "
          "......export_file_name")
    sys.exit(0)
else:
    filename = sys.argv[1:]
    #store export file name
    export_file = filename[-1]

    filename = filename[:-1]
    for file in filename:
        if '.vcf.gz' not in file or '.vcf' not in file:
            print("Please provide vcf files only")
            sys.exit(0)

mutation_change_dict = dict()
exportfile = open(export_file + '.txt', 'w')




# iterate through each file
for file in filename:
    exportfile.write(file[:file.index('.')])
    exportfile.write('\n')

    #write header for file
    header = subprocess.check_output('gunzip -c ' + filename[0] + '| grep \'#CHROM\'', shell=True).splitlines()
    if len(header) > 1:
        header = header[0].decode('utf-8').split('\t')[:5]
        exportfile.write(','.join(header))
        exportfile.write('\n')

        # extract element with novoPP >= 0.9 only from vcf files
        if '.vcf.gz' in file:
            mutation_list = subprocess.check_output('gunzip -c ' + file + '| grep \'novoPP=0.9\'', shell=True).splitlines()
            # iterate through each mutation obtained from grep
            for mutation in mutation_list:
                # decode the into string and extract the mutation elements
                mutation = mutation.decode('utf-8').split('\t')
                mutation = mutation[:5]
                print(mutation)
                exportfile.write(','.join(mutation))
                exportfile.write('\n')
                mutation_change = ' > '.join(mutation[-2:])
                if mutation_change in mutation_change_dict:
                    mutation_change_dict[mutation_change] += 1
                else:
                    mutation_change_dict[mutation_change] = 1

            exportfile.write('\n')
exportfile.close()


print(mutation_change_dict)



