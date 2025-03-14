from insert_text import readfile_and_insert_contents, writefile
from get_filelist import get_filepath_list
import sys

# Insert File To Modify

FileList = get_filepath_list()
input_text = "# Referensi Produk \n\n"

for file_path in FileList:
    # file
    if "Referensi Produk" in file_path:
        try:
            file_contents = readfile_and_insert_contents(file=file_path, text=input_text)
            writefile(file=file_path,contents=file_contents)
            print(file_path)
            print("File Sucessfully Modified")
        except Exception as err:
            print(err)