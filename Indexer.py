import os

path = "documents/"
all_lines = []
files_in_directory = os.listdir(path)

for files in files_in_directory:
    with open(os.path.join(path+files), 'r', encoding='utf-8') as file:
        doc = file.read().split('\n', 1)
        print(doc)

# for lines in all_lines:
#     for line in range(len(lines)):
#         print(lines[line])
