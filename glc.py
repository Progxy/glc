import os
import sys
from enum import Enum

class CommentType(Enum):
    MULTI_LINE = 1
    SINGLE_LINE = 2
    NO_COMMENT = 3
    C_STYLE = 4
    PY_STYLE = 5
    ASM_STYLE = 6
    HTML_STYLE = 7

def is_valid_ext(filename, valid_exts):
    for valid_ext in valid_exts:
        if filename.endswith(valid_ext):
            return True
    return False

def read_folder(folder_name, valid_exts):
    file_names = []
    # Check if the directory exists
    if not os.path.isdir(folder_name):
        print(f"The specified directory {directory} does not exist.")
        return file_names

    # Loop through all files in the directory
    for filename in os.listdir(folder_name):
        file_path = os.path.join(folder_name, filename)

        # Check if it's a file (not a directory)
        if os.path.isfile(file_path) and is_valid_ext(filename, valid_exts):
            file_names.append(file_path)
        elif os.path.isdir(file_path):
            file_names += read_folder(file_path, valid_exts)
            
    return file_names

def is_non_commented_line(line, file_comment_type):
    comments = {CommentType.PY_STYLE : "#", CommentType.ASM_STYLE : ";", CommentType.C_STYLE: "//"}
    multi_line_comments_starts = {CommentType.C_STYLE: "/*", CommentType.HTML_STYLE: "<!--", CommentType.PY_STYLE : "'''", CommentType.PY_STYLE : "\"\"\""}
    multi_line_comments_ends = {CommentType.C_STYLE: "*/", CommentType.HTML_STYLE: "-->", CommentType.PY_STYLE: "'''", CommentType.PY_STYLE : "\"\"\""}
    line = line.strip()
    for comment_type in comments:
        if line.startswith(comments[comment_type]) and comment_type == file_comment_type:
            return CommentType.SINGLE_LINE
    for comment_type in multi_line_comments_starts:
        comment_start = multi_line_comments_starts[comment_type]
        comment_end = multi_line_comments_ends[comment_type]
        if line.startswith(comment_start) and line.endswith(comment_end) and comment_type == file_comment_type:
            return CommentType.SINGLE_LINE
        elif line.startswith(comment_start) or line.endswith(comment_end) and comment_type == file_comment_type:
           return CommentType.MULTI_LINE
    return CommentType.NO_COMMENT

def get_comment_type(file_name):
    if file_name.endswith(".py"):
        return CommentType.PY_STYLE
    elif file_name.endswith(".html"):
        return CommentType.HTML_STYLE
    elif file_name.endswith(".asm") or file_name.endswith(".s") or file_name.endswith(".S"):
        return CommentType.ASM_STYLE
    else:
        return CommentType.C_STYLE

def count_lines(file_names, verbose):
    files_commented_lines = 0
    files_loc = 0
    is_multi_comment_enabled = False
    max = 0
    if not verbose:
        for file_name in file_names: 
            if max < len(file_name):
                max = len(file_name)
        spaces = max - 9
        print(f"File Name {spaces * ' '}| File Lines | File LoCs | File Commented Lines")
    for file_name in file_names:
        file_commented_lines = 0
        file_loc = 0
        comment_type = get_comment_type(file_name)
        with open(file_name, 'r') as file: 
            file_content = file.read()
            is_inside_string = False
            for i in range(0, len(file_content)):
                char = file_content[i]
                if char == '\'' or char == '"' or char == '`':
                    is_inside_string = not is_inside_string
                elif char == '\r' or char == '\n' and is_inside_string:
                    char = ''
            lines = file_content.replace("\n", "\r").split("\r")
            
            for line in lines:
                if is_multi_comment_enabled and is_non_commented_line(line, comment_type) == CommentType.MULTI_LINE:
                    file_commented_lines += 1
                    is_multi_comment_enabled = False
                elif is_multi_comment_enabled:
                    file_commented_lines += 1
                elif is_non_commented_line(line, comment_type) == CommentType.SINGLE_LINE:
                    file_commented_lines += 1
                else:
                    file_loc += 1
        if verbose:
            print(f"{file_name} contains {file_loc + file_commented_lines} lines which are divided in {file_loc} LoCs and {file_commented_lines} commented lines")
        else:
            spaces = max - len(file_name)
            total_space = 10 - len(str(file_loc + file_commented_lines))
            loc_space = 9 - len(str(file_loc))
            print(f"{file_name} {spaces * ' '}| {file_loc + file_commented_lines} {total_space * ' '}| {file_loc} {loc_space * ' '}| {file_commented_lines}")
        files_commented_lines += file_commented_lines
        files_loc += file_loc
    if verbose:
        print(f"This project contains in total {files_loc + files_commented_lines} lines, which are divided in: {files_loc} LoCs and {files_commented_lines} commented lines")
    else:
        print(f"{50 * '-'}")
        print(f"Total Lines | Total LoCs | Total Commented Lines")
        total_space = 11 - len(str(files_loc + files_commented_lines))
        loc_space = 10 - len(str(files_loc))
        print(f"{files_loc + files_commented_lines} {total_space * ' '}| {files_loc} {loc_space * ' '}| {files_commented_lines}")
    return

def print_helper():
    print("Usage glc.py [flag=value]:")
    print("\t-d: set the directory to inspect, e.g.: glc.py -d=mydir.")
    print("\t-e: set the extensions that should be considered, passing them has a list divided by commas, e.g.: glc.py -e=.c,\".h\",'.cpp',...")
    print("\t-v: set verbose mode.")
    print("\t-h: show the help.")
    print("Note: when passing multiple flags the program will consider only the last one provided for each flag-type.")
    return

def parse_args():
    directory = ""
    valid_exts = []
    verbose = False
    
    if len(sys.argv) < 2: 
        print("No arguments passed.")
        print_helper()
        exit(1)

    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if (arg.startswith("-d=")):
            directory = arg.replace("-d=", "").replace("\"", "").replace("'", "")
        elif (arg.startswith("-e=")):
            valid_exts = arg.replace("-e=", "").replace("\"", "").replace("'", "").split(",")
        elif (arg.startswith("-h")):
            print_helper()
            exit(1)
        elif (arg.startswith("-v")):
            verbose = True
        else:
            print("Invalid argument.")
            print_helper()
            exit(1)
 
    if (len(valid_exts) == 0):
        print("No exts passed.")
        print_helper()
        exit(1)
    elif (directory == ""):
        print("No directory passed.")
        print_helper()
        exit(1)
    
    return directory, valid_exts, verbose

if __name__ == '__main__':
    directory, valid_exts, verbose = parse_args()
    file_names = read_folder(directory, valid_exts)
    if len(file_names) == 0:
        print(f"Found 0 files in {directory}, considering files with these extensions: {valid_exts}")
        exit(0)
    count_lines(file_names, verbose)

