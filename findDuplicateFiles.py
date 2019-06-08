import os
import hashlib
import collections


def traversePath(directory, filechecksums):

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
                    filechecksums[hash_md5].append(file_path)
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
                traversePath(sub_dir, filechecksums)


exclude_paths = ['c:\\$Recycle.Bin', 'c:\\hp']
checksums = collections.defaultdict(list)
traversePath('c:\\', checksums)

with open('c:\\temp\\duplicate_files_driveC.txt', 'w', encoding="utf-8") as log:
    for key, value in checksums.items():
        log.write('%s: %s :%d\n' % (key, value, len(value)))
        print('{}: {}'.format(key, value))
        log.flush()
