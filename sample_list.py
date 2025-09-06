import os

for root, dirs, files in os.walk(os.path.abspath("/path/to/your/reads/")):
    for file in files:
        if file.endswith(".gz"):
            print(os.path.join(root, file))
