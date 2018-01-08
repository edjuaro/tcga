from dfm_functions import *
import argparse

parser = argparse.ArgumentParser()
# ~~~~Arguments~~~~~ #
parser.add_argument("-m", "--manifest", type=str,
                    help="The relative path of the manifest used to download the data")
parser.add_argument("-n", "--metadata", type=str,
                    help="The relative path of the metadata file")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
args = parser.parse_args()
if args.verbose:
    print("We like being verbose!")


# Download from manifest
# manifest = "gdc_manifest_20171221_005438.txt"
manifest = args.manifest
# metadata_file = "metadata.cart.2017-12-21T21_41_22.870798.json"
metadata_file = args.metadata

command = "./gdc-client download -m "+manifest
print("About to execute the command:", command)
what = execute(command)
print('All files in manifest were downloaded, probably. To be sure, check the output of the gdc-client.')

dfest = pd.read_table(manifest)

# Parse metadata
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
