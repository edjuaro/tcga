from subprocess import call
manifest = "gdc_manifest_20171221_005438.txt"
command = "./gdc-client download -m "+manifest
call(command, shell=True)
