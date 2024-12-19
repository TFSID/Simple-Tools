def readfile_and_insert_contents(file, text):
    # open the file
    with open(file, 'r') as file:
        try:
            contents = file.readlines() # reads every line into a list of lines
        except Exception as err:
            print(err)
    contents.insert(0,text)
    print(contents)
    return contents

def writefile(output,contents):
    with open(output, 'w') as output:
        try:
            output.writelines(contents)
            return "Content Writed Into File"
        except Exception as err:
            print(err)
    # insert a text into array or list of text that have been read before from the file

input_file = "example.md"
input_text= "# Referensi Layanan"
file_out="out.md"
input_content = readfile_and_insert_contents(file=input_file,text=input_text)

writefile(output=file_out,contents=input_content)
# readfile_and_insert_contents(file=input_file,text=input_text)

