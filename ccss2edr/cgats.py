from collections.abc import Mapping
import shlex


class CGATS(Mapping):
    def __init__(self, file):
        self.filetype = None
        self.params = {}
        self.data = []
        self.data_format = []
        self.keywords = []

        self.read(file)

    def read(self, file):
        read_first_line = False
        parsing_data = False
        parsing_data_format = False

        for line in file:
            tok = shlex.split(line)

            if not read_first_line:
                self.filetype = tok
                read_first_line = True
                continue

            if not tok:
                continue

            if tok[0] == 'KEYWORD':
                self.keywords.append(tok[1])
            elif tok[0] == 'BEGIN_DATA':
                parsing_data = True
            elif tok[0] == 'END_DATA':
                parsing_data = False
            elif tok[0] == 'BEGIN_DATA_FORMAT':
                parsing_data_format = True
            elif tok[0] == 'END_DATA_FORMAT':
                parsing_data_format = False
            elif parsing_data:
                self.data.append(tok)
            elif parsing_data_format:
                self.data_format = tok
            else:
                self.params[tok[0]] = tok[1]

    def __getitem__(self, key):
        return self.params[key]

    def __iter__(self):
        return iter(self.params)

    def __len__(self):
        return len(self.params)
