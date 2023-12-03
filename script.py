# Имена файлов, подлежащих удалению.
FILES_FOR_DELETE = [
    'example.txt',
]

# Шаблоны файлов, подлежащих переименованию.
# Примеры:
#   abc*    : 'abc 123.txt' => '123.txt'
#   *123    : 'abc 123.txt' => 'abc.txt'
#   aa*cc   : 'aa bbb cc.txt' => 'bbb.txt'
#   *111*   : 'aa111bb.txt' => 'aabb.txt'
#   1*3*5   : '12345.txt' => '24.txt'
#   \*\**   : '**abc.txt' => 'abc.txt'
FILES_FOR_RENAME = [
    '*example',
]

# Путь к корневой папке (от которой нужно начинать поиск файлов).
# Может быть относительным или абсолютным.
BASE_PATH = '.'

# ======================================================================

import re
from pathlib import Path
from argparse import ArgumentParser

class DeleteAction:
    def __init__(self) -> None:
        self.removed_files = []

    def process(self, file: Path) -> None:
        if file.is_file() and file.name in FILES_FOR_DELETE: 
            file.unlink(missing_ok=True) 
            self.removed_files.append(file)

    def print_result(self) -> None:
        print('Удалённые файлы:', *self.removed_files, sep='\n')

class RenameAction:
    def __init__(self) -> None:
        self.renamed_files = []
        self.patterns = [re.sub(r'([!"%\',/:;<=>@`_])|(\\+)\*', self._repl, re.escape(pattern)) for pattern in FILES_FOR_RENAME]        

    def process(self, file: Path) -> None:
        if not file.is_file():
            return
        
        for p in self.patterns:
            name, dot, extension = file.name.rpartition('.')
            match = re.fullmatch(p, name)
            if match is not None:
                new_file = file.replace(file.with_name(''.join(match.groups()).strip() + dot + extension))
                self.renamed_files.append((file, new_file))
                break

    def print_result(self) -> None:
        print('Переименованные файлы:', *[str(old) + ' => ' + str(new) for old, new in self.renamed_files], sep='\n')

    @staticmethod
    def _repl(m: re.Match):
        if m[1] is not None:
            return rf'\{m[1]}'
        return '(.*)' if m[2] == '\\' else '\*'


parser = ArgumentParser()
parser.add_argument("-d", "--no-delete", dest="no_delete", default=False, action='store_true', help="Не удалять файлы")
parser.add_argument("-r", "--no-rename", dest="no_rename", default=False, action='store_true', help="Не переименовывать файлы")
args = parser.parse_args()

actions = []
if not args.no_delete:
    actions.append(DeleteAction())
if not args.no_rename:
    actions.append(RenameAction())

for file in Path(BASE_PATH).rglob('*'):
    for action in actions:
        action.process(file)

for action in actions:
    action.print_result()
    print()
