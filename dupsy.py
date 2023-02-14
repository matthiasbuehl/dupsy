import os
import io
import hashlib
import re
import pdb

exclude_list = ['.DS_Store']

class Dupsy:
    def __init__(self, folder_a=None, folder_b=None, extensions=None):
        self.extensions = extensions
        self.folder_a = folder_a
        self.folder_b = folder_b
        self.files_a = {}
        self.files_b = {}


    def file_is_considered(self, file_name):
        if file_name in exclude_list:
            return False

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

    def index(self):
        if not self.folder_a is None:
            self.files_a = self.search_dir(self.folder_a)
        if not self.folder_b is None:
            self.files_b = self.search_dir(self.folder_b)

    def search_dir(self, dir_path):
        if not dir_path:
            return

        files = {}

        for dir_name, subdir_list, file_list in os.walk(dir_path):
            for file_name in file_list:
                if self.file_is_considered(file_name):
                    full_path = os.path.join(dir_name, file_name)
                    self._print_ln(full_path)
                    self.add_file(files, full_path)
            self._print_ln("")

        return files

    def _print_ln(self, text):
        print("\33[2K\r", end="")
        print(text, end="\r")

    def add_file(self, files_dict, full_path):
        file_hash = self.hash_file(full_path)

        if file_hash in files_dict.keys():
            if not full_path in files_dict[file_hash]:
                files_dict[file_hash].append(full_path)
        else:
            files_dict[file_hash] = [full_path]

    def dups_in_a(self):
        return self.dups(self.files_a)


    def dups_in_b(self):
        return self.dups(self.files_b)


    def dups(self, file_dict):
        file_paths_map = {}

        for file_name, file_paths in file_dict.items():
            if len(file_paths) > 1:
                file_paths_map[file_name] = file_paths

        return file_paths_map

    def dup_report(self, show_a=True, show_b=False):
        if show_a:
            print("dups in a")
            self._dup_report(self.files_a)

        if show_b:
            print("dups in b")
            self._dup_report(self.files_b)

    def _dup_report(self, file_paths_map):
        for sha, paths in self.dups(file_paths_map).items():
            print(f'# {sha}')

            found_suspects = False
            prefix = ""

            for path in paths:
                if self._is_dup_suspect(path):
                    prefix = ""
                    found_suspects = True
                else:
                    prefix = "# "
                print(f'{prefix}rm "{path}"')

            if not found_suspects:
                print("# NO SUSPECTS")

            print("\n")


    def _is_dup_suspect(self, path):
        return re.search(r'\(\d\)', path) is not None

    def dup_paths_a(self):
        return self._dup_paths(self.dups(self.files_a))

    def dup_paths_b(self):
        return self._dup_paths(self.dups(self.files_b))

    def _dup_paths(self, file_paths_map):
        return [path for paths in list(file_paths_map.values()) for path in paths]

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

# ^((?!\(\d\)).)*$

d = Dupsy()
d.folder_a = "/Users/mbuehl/Dropbox/Photos/2004"
d.folder_b = "/Volumes/photo/2004"
d.index()
# print(d.dups_in_a())
# print(d.dup_paths_a())
# print(d.dups_in_b())
# print(d.dup_paths_b())
d.dup_report()