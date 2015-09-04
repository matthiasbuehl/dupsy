import os
import io
import hashlib
import re
import pdb

class Dupsy:
    def __init__(self, folder_a=None, folder_b=None, extensions=None):
        self.extensions = extensions
        self.folder_a = folder_a
        self.folder_b = folder_b
        self.files_a = self.search_dir(folder_a)
        self.files_b = self.search_dir(folder_b)


    def file_is_considered(self, file_name):
        if self.extensions is None:
            return True

        pattern = '\.%s$' % '|'.join(self.extensions)
        return re.search(pattern, file_name, re.IGNORECASE)

     
    def hash_file(self, file_path, buffer_size=io.DEFAULT_BUFFER_SIZE):
        with open(file_path, 'rb') as f:
            md5 = hashlib.md5()
            
            for chunk in iter(lambda: f.read(buffer_size), b''):
                md5.update(chunk)

        return md5.hexdigest()


    def search_dir(self, dir_path):
        if not dir_path:
            return

        files = {}

        for dir_name, subdir_list, file_list in os.walk(dir_path):
            for file_name in file_list:
                if self.file_is_considered(file_name):
                    full_path = os.path.join(dir_name, file_name)
                    print full_path
                    self.add_file(files, full_path)

        return files


    def add_file(self, files_dict, full_path):
        file_hash = self.hash_file(full_path)

        if file_hash in files_dict.keys():
            files_dict[file_hash].append(full_path)
        else:
            files_dict[file_hash] = [full_path]

    """
    def dups_in_a(self):
        return self.dups(self.files_a)


    def dups_in_b(self):
        return self.dups(self.files_b)


    def dups(self, file_dict):
        dup_files = {}

        for file_name, file_paths in file_dict.iteritems():
            if len(file_paths) > 1:
                dup_files[file_name] = file_paths

        return dup_files
    """


    def a_only(self):
        return self.left_unique(self.files_a, self.files_b)


    def b_only(self):
        return self.left_unique(self.files_b, self.files_a)


    def left_unique(self, files_left, files_right):
        files_left_only = {}
        left_only_keys = set(files_left.keys()) - set(files_right.keys())

        for left_key in left_only_keys:
            files_left_only[left_key] = files_left[left_key]

        return files_left_only


    def a_and_b(self):
        files_in_both = {}
        common_keys = set(self.files_a.keys()) & set(self.files_b.keys())

        for key in common_keys:
            files_in_both[key] = self.files_a[key]
            files_in_both[key].extend(self.files_b[key])

        return files_in_both



import pprint 
pp = pprint.PrettyPrinter(indent=4)

d = Dupsy(
    folder_a='/Volumes/photo',
    folder_b='/Users/mbuehl/Dropbox/Photos',
    extensions=['jpg', 'mov']
)
"""
print 'A'
pp.pprint(d.files_a)
print 'B'
pp.pprint(d.files_b)
"""
print 'LEFT ONLY'
pp.pprint(d.a_only())
print 'RIGHT ONLY'
pp.pprint(d.b_only())
print 'BOTH'
pp.pprint(d.a_and_b())