import os

for root, dirs, files in os.walk(os.path.abspath("/gpfs/scratch/akwakye/Warfle_22_23_24/F24A430001458_LIBucnlR/")):
    for file in files:
        if file.endswith(".gz"):
            print(os.path.join(root, file))
