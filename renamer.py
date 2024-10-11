import os
import sys

# Define the base directory where the renaming should start
base_dir = "akasata-docs//docs/Product List/"
for root, dirs, files in os.walk(base_dir):
    # melakukan pengecekan terhadap current direktori
    # current_dir = root, dirs[0]
    # sys.exit(current_dir)

    # Melakukan listing terhadap file yang terdapat pada setiap direktori
    for dir in dirs:
        current_dir = os.path.join(root, dir)
        file_list = [files for root, dirs, files in os.walk(current_dir)][0]
        # Melakukan Pencarian Terhadap file bernam README.md pada direktori menggunakan for loop
        for file in file_list:
            if file == "README.md":
                new_file_name = f"Ide Layanan.md"
                current_file_path = os.path.join(current_dir, file)
                new_file_path = os.path.join(current_dir, new_file_name)
                # sys.exit(current_file_path)
                os.rename(current_file_path, new_file_path)
                
                # mecegah looping
                # sys.exit("oke")
                print(f'Renamed {current_dir}"README.md" > Ide Layanan.md')

# Traverse through the base directory