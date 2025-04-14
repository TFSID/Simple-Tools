from insert_text import readfile_and_insert_contents, writefile
from get_filelist import get_filepath_list
import argparse
import json
import sys

# Insert File To Modify
def data_modification(file, text_to_replace):
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

def text_extraction(file, keyword):
    print("To Be Continued")

def json_extraction(file, keyword:str, output):
    with open(file, "r") as f:
        key = json.loads(f.read())
        results = []
        for data in key["data"]:
            # results.append(data["Website"])
            results.append(data[keyword])
            # print(data["Website"])
    try:
        print(f"saving results at {output}")
        with open(output, "w") as out:
            for sites in results:
                out.write(f"{sites}\n")
    except Exception as err:
        print(f"results not saved because of {err}")
        sys.exit()

def parse_args():
    parser = argparse.ArgumentParser(description="This Is Some Data/File Manipulator/Modifier")
    parser.add_argument("--keyword", type=str, help="input keyword to search in a file", required=False)
    parser.add_argument("--file", help="input file to be processed")
    parser.add_argument("--output", help="Output file destination")

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    # text_extraction(args.file, args.keyword)
    json_extraction(args.file, args.keyword, args.output)
