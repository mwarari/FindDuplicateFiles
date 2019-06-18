''' This script goes through a path on filesystem and returns a list of duplicate files.

    The script does this by creating an md5 hash on each file and creating a hash with the key as the md5 hash.
    The value is the file with full path.

    Usage:
        python findDuuplicateFiles.py paths=Paths [exlude_paths=ExcludePaths] [output_file=OutputFile]

        Arguments:
            paths:                   Paths to scan
            exclude_paths(optional): Paths to exclude from scan
            output_file(Optional):   The file to send the results to.

        Example:
             python findDuuplicateFiles.py paths=C:\,D:\ exlude_path=C:$Recycle.bin,c:\pin [output_file=c:\temp\duplicate_files.txt]

    Output:
        The contents look something like this:
            md5Hash: ['duplicate_file_1', 'duplicate_file_2'] :2

    Limitations:
        Python does not provide for a way to control memory allocation, so there are files that may be too large to read
        and calculate the md5hash. These will produce a 'Memory error reading: {name of file}' error to standard output.
'''

import os
import hashlib
import collections
import sys


def traverse_path(directory, file_checksums):
    for r, d, f in os.walk(directory):
        ''' Check if the path is one of the paths to be excluded '''
        do_search = True
        for exclude in exclude_paths:
            if exclude in r:
                do_search = False

        if do_search:
            for file in f:
                file_path = os.path.join(r, file)

                try:
                    hash_md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                    print('{}: {}'.format(file_path, hash_md5))
                    file_checksums[hash_md5].append(file_path)
                except PermissionError:
                    print('Could not read: {}'.format(file_path))
                except FileNotFoundError:
                    print('Could not find: {}'.format(file_path))
                except MemoryError:
                    print("Memory Error reading: {}".format(file_path))
                except OSError as error:
                    print("OS Error: {} Error reading: {}".format(error, file_path))

        for sub_dir in d:
            if sub_dir not in exclude_paths:
                traverse_path(sub_dir, file_checksums)


def traverse_paths(directories, filechecksums):
    for directory in directories:
        traverse_path(directory, filechecksums)


def get_command_line_argument(arg_name):
    if len(sys.argv) == 1:
        return None
    for arg in sys.argv:
        split_arg = arg.split('=')
        if len(split_arg) > 1:
            if split_arg[0].upper() == arg_name.upper():
                return split_arg[1]

    return None


def show_usage():
    this_file = os.path.basename(__file__)
    print('''
    Usage:
        python {} paths=Paths [exlude_paths=ExcludePaths] [output_file=OutputFile]

        Arguments:
            paths:                    Paths to scan
            exclude_paths (optional): Paths to exclude from scan
            output_file (Optional):   The file to send the results to.

        Example:
             python {} paths=C:\\,D:\\ exlude_path=C:$Recycle.bin,c:\\pin [output_file=c:\\temp\\duplicate_files.txt]
    '''.format(this_file, this_file))


tmp = get_command_line_argument('paths')
if tmp is None:
    show_usage()
    exit(1)
else:
    paths = tmp.split(',')

tmp = get_command_line_argument('exclude_paths')
if tmp is None:
    exclude_paths = []
else:
    exclude_paths = tmp.split(',')

tmp = get_command_line_argument('output_file')
if tmp is None:
    output_file = ''
else:
    output_file = tmp

# output_file = get_command_line_argument('output_file')
duplicates = collections.defaultdict(list)
traverse_paths(paths, duplicates)

if output_file != '':
    with open(output_file, 'w', encoding="utf-8") as log:
        for key, value in duplicates.items():
            log.write('%s: %s :%d\n' % (key, value, len(value)))
            log.flush()
else:
    for key, value in duplicates.items():
        print('%s: %s :%d\n' % (key, value, len(value)))
