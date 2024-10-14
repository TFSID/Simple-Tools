import sys
import os

def readfile_and_insert_contents(file, text):
    # open the file
    with open(file, 'r') as file:
        try:
            contents = file.readlines() # reads every line into a list of lines
        except Exception as err:
            print(err)
    contents.insert(0,text + '\n\n')
    return contents

def writefile(file,contents):
    with open(file, 'w') as file:
        try:
            file.writelines(contents)
            print("Content Writed Into File")
        except Exception as err:
            print(err)
    # insert a text into array or list of text that have been read before from the file

input_file = "example.md"
input_text= "# Referensi Layanan"
input_content = readfile_and_insert_contents(file=input_file,text=input_text)

writefile(input_file,contents=input_content)

