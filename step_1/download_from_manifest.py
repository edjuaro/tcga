import subprocess
from subprocess import call
import pandas as pd
import os
import shutil
import gzip
import json
import sys


def uncompress_gzip(file_name, new_name=None, delete=True):
    # Read the stream and write that stream to a new file:
    in_file = gzip.open(file_name, 'rb')
    if new_name is None:
        out_file = open(file_name.strip('.gz'), 'wb')
    else:
        out_file = open(new_name, 'wb')
    out_file.write(in_file.read())
    in_file.close()
    out_file.close()
    if delete:
        os.remove(file_name)


def execute(comando, doitlive=False, input_to_use=None):
    # result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
    comando = comando.split(' ')

    if doitlive:
        popen = subprocess.Popen(comando, stdout=subprocess.PIPE, universal_newlines=True)
        to_return = popen.stdout.read()
        for line in to_return:
            print(line, end='')
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, comando)
    else:
        if input_to_use is not None:
            input_to_use = input_to_use.ecode('utf-8')
        result = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=input_to_use)
        to_return = result.stdout.decode('utf-8')
        print(to_return)
    return to_return.strip('\n')


# Download from manifest
manifest = "gdc_manifest_20171221_005438.txt"
command = "./gdc-client download -m "+manifest
what = execute(command)
print('All files in manifest were downloaded, probably. To be sure, check the output of the gdc-client.')

dfest = pd.read_table(manifest)

# Parse metadata
metadata_file = "metadata.cart.2017-12-21T21_41_22.870798.json"
meta_data = json.load(open(metadata_file))

# Make a dictionary to map file names to TCGA unique ID's
#   # if we wanted to have only one sample per patient per "phenotype" we could use this:
#   # meta_data[0]['cases'][0]['samples'][0]['submitter_id']
#   # But since we want a unique ID for each HTSeq file (some patient/phenotypes will have multiple vials/replicates):
#   # meta_data[0]['cases'][0]['samples'][0]['portions'][0]['analytes'][0]['aliquots'][0]['submitter_id']
#   # Read more hre: https://wiki.nci.nih.gov/display/TCGA/Understanding+TCGA+Biospecimen+IDs
name_id_dict = {}
for i in range(len(meta_data)):
    file_name = meta_data[i]['file_name']
    unique_id = meta_data[i]['cases'][0]['samples'][0]['portions'][0]['analytes'][0]['aliquots'][0]['submitter_id']
    name_id_dict[file_name] = unique_id

# pwd = os.path.dirname(__file__)
pwd = execute('pwd', doitlive=True)
destination = os.path.join(pwd, 'raw_files')
if not os.path.isdir(destination):
    os.mkdir(destination)

for d, f in zip(dfest['id'], dfest['filename']):
    shutil.copy(os.path.join(d, f), destination)  # Move the downloaded files to a folder
    shutil.rmtree(d)  # Remove those files/folders from current directory
    # "decompress" and remove gz files
    uncompress_gzip(os.path.join(destination, f), new_name=os.path.join(destination, name_id_dict[f]))
print('All files were moved and "decompressed" successfully.')
