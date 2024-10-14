import os 
import sys


def get_filepath_list():
    base_dir = "..//akasata-docs//docs/Product List/"
    file_path_list = []

    # Melakukan Looping Pada Base Direktori Untuk Mencari Isi Yang Terdapat Pada Direktori Tersebut
    for root, dirs, files in os.walk(base_dir):

        # Looping Untuk Menampilkan List Direktori Yang Telah Didapat Pada variable dirs
        for dir in dirs:
            dir_name = os.path.join(root, dir)

            for product_root, product_dirs, product_files in os.walk(dir_name): 
                # file_list = [file for file in product_files]
                
                # Get File Recursivly After Get Into The Directories
                # Appending Every File Path Into A List
                for file in product_files:
                    file_path_list.append(os.path.join(dir_name, file))
    return file_path_list
