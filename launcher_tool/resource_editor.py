#!python
"""\
Use Windows API to change resources in exe/dll's.
"""
import argparse
import ctypes
import itertools
import struct
import sys
from pprint import pprint

from ctypes.wintypes import HANDLE, HMODULE, HRSRC, HGLOBAL
from ctypes.wintypes import BOOL
from ctypes.wintypes import LPCWSTR, LPWSTR, LPVOID
from ctypes.wintypes import BYTE, WORD, DWORD


LOAD_LIBRARY_AS_DATAFILE = 2
RT_STRING = 6

resource_types = {
    1: 'RT_CURSOR',
    2: 'RT_BITMAP',
    3: 'RT_ICON',
    4: 'RT_MENU',
    5: 'RT_DIALOG',
    6: 'RT_STRING',
    7: 'RT_FONTDIR',
    8: 'RT_FONT',
    9: 'RT_ACCELERATOR',
    10: 'RT_RCDATA',
    11: 'RT_MESSAGETABLE',
    12: 'RT_GROUP_CURSOR',
    14: 'RT_GROUP_ICON',
    16: 'RT_VERSION',
    17: 'RT_DLGINCLUDE',
    19: 'RT_PLUGPLAY',
    20: 'RT_VXD',
    21: 'RT_ANICURSOR',
    22: 'RT_ANIICON',
    23: 'RT_HTML',
    24: 'RT_MANIFEST',
}


def ValidHandle(value):
    if value == 0:
        raise ctypes.WinError()
    return value
check_bool = ValidHandle

LoadLibraryEx = ctypes.windll.kernel32.LoadLibraryExW
LoadLibraryEx.argtypes =  [LPCWSTR, HANDLE, DWORD]
LoadLibraryEx.restype = ValidHandle

LoadResource = ctypes.windll.kernel32.LoadResource
LoadResource.argtypes =  [HMODULE, HRSRC]  # hModule,  hResInfo
LoadResource.restype = ValidHandle

FindResourceEx = ctypes.windll.kernel32.FindResourceExW
#~ FindResourceEx.argtypes =  [HMODULE, LPCTSTR, LPCTSTR, WORD]  # hModule, lpType, lpName, wLanguage
FindResourceEx.argtypes =  [HMODULE, ctypes.c_int, ctypes.c_int, WORD]  # hModule, lpType, lpName, wLanguage
FindResourceEx.restype = ValidHandle

SizeofResource = ctypes.windll.kernel32.SizeofResource
SizeofResource.argtypes =  [HMODULE, HRSRC]  # hModule,  hResInfo
SizeofResource.restype = DWORD

LockResource = ctypes.windll.kernel32.LockResource
LockResource.argtypes =  [HGLOBAL]  # hResData
LockResource.restype = ctypes.c_void_p

#~ EnumResTypeProc = ctypes.CFUNCTYPE(BOOL, HMODULE, LPTSTR, LONG_PTR) # hModule lpszType lParam
EnumResTypeProc = ctypes.CFUNCTYPE(BOOL, HMODULE, ctypes.c_int, ctypes.c_int) # hModule lpszType lParam

EnumResourceTypes = ctypes.windll.Kernel32.EnumResourceTypesW
EnumResourceTypes.argtypes = [HMODULE, EnumResTypeProc, ctypes.c_int] # hModule, lpEnumFunc, lParam
EnumResourceTypes.restype = check_bool


#~ EnumResNameProc = ctypes.CFUNCTYPE(BOOL, HMODULE, LPCWSTR, LPWSTR, ctypes.c_int) # hModule, lpszType, lpszName, lParam
EnumResNameProc = ctypes.CFUNCTYPE(BOOL, HMODULE, ctypes.c_int, ctypes.c_int, ctypes.c_int) # hModule, lpszType, lpszName, lParam

EnumResourceNames = ctypes.windll.kernel32.EnumResourceNamesW
#~ EnumResourceNames.argtypes = [HMODULE, LPCWSTR, EnumResNameProc, ctypes.c_int] # hModule, lpszType, lpEnumFunc, lParam
EnumResourceNames.argtypes = [HMODULE, ctypes.c_int, EnumResNameProc, ctypes.c_int] # hModule, lpszType, lpEnumFunc, lParam
EnumResourceNames.restype = check_bool

# hModule, lpszType,lpszName, wIDLanguage, lParam
#~ EnumResLangProc = ctypes.CFUNCTYPE(BOOL, HMODULE, LPCTSTR, LPCTSTR, WORD, LONG_PTR)
EnumResLangProc = ctypes.CFUNCTYPE(BOOL, HMODULE, ctypes.c_int, ctypes.c_int, WORD, ctypes.c_int)

EnumResourceLanguages = ctypes.windll.kernel32.EnumResourceLanguagesW
#~ EnumResourceLanguages.argtypes = [HMODULE, LPCTSTR, LPCTSTR, EnumResLangProc, LONG_PTR]
EnumResourceLanguages.argtypes = [HMODULE, ctypes.c_int, ctypes.c_int, EnumResLangProc, ctypes.c_int]  # hModule, lpType, lpName, lpEnumFunc, lParam
EnumResourceLanguages.restype = check_bool


UpdateResource = ctypes.windll.kernel32.UpdateResourceW
#~ UpdateResource.argtypes = [HANDLE, LPCWSTR, LPCWSTR, WORD, LPVOID, DWORD] # hUpdate  lpType  lpName wLanguage lpData cbData
UpdateResource.argtypes = [HANDLE, ctypes.c_int, ctypes.c_int, WORD, ctypes.POINTER(ctypes.c_ubyte), DWORD] # hUpdate  lpType  lpName wLanguage lpData cbData
UpdateResource.restype = BOOL

BeginUpdateResource = ctypes.windll.kernel32.BeginUpdateResourceW
BeginUpdateResource.argtypes = [LPCWSTR, BOOL] # pFileName  bDeleteExistingResources
BeginUpdateResource.restype = HANDLE

EndUpdateResource = ctypes.windll.kernel32.EndUpdateResourceW
EndUpdateResource.argtypes = [HANDLE, BOOL] # hUpdate  fDiscard
EndUpdateResource.restype = BOOL

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def decode_string_table_bundle(table):
    """Decode a bundle of 16 strings from a resource"""
    (first_index,) = struct.unpack(b'<H', table[:2])
    strings = [u'' for i in range(16)]
    pos = 2
    for i in range(16):
        if pos + 1 > len(table): break
        (length,) = struct.unpack(b'<H', table[pos : pos + 2])
        pos += 2
        strings[i] = table[pos : pos + length*2].decode('utf-16')
        #~ print i, table[pos :]
        pos += length*2
    return first_index, strings

def encode_string_table_bundle(first_index, strings):
    """Encode a bundle of 16 strings for a resource"""
    if len(strings) != 16: raise ValueError('strings must have 16 entries')
    table = bytearray()
    table.extend(struct.pack(b'H', first_index))
    for s in strings:
        table.extend(struct.pack(b'H', len(s)))
        table.extend(s.encode('utf-16le'))
    return table


class StringTable(object):
    """\
    Handle a bunch of strings that are identified by a number. Multiple
    variants for different Languages.
    
    In the resource files they are ordered a bit different, here we start
    with the language and each of them has a map of all the strings.
    """
    def __init__(self):
        self.languages = {}

    def load_from_resource(self, res):
        self.languages = {}
        for name in res.enumerate_names(RT_STRING):
            for lang in res.enumerate_languages(RT_STRING, name):
                id, strings = decode_string_table_bundle(
                    res.get_resource(RT_STRING, name, lang))
                d = self.languages.setdefault(lang, {})
                for n, s in enumerate(strings, id + (name - 1) * 16):
                    if s:
                        d[n] = s

    def save_to_resource(self, res):
        # find out which IDs are in use
        all_ids = set(n for n, text in itertools.chain.from_iterable(lang.items() for lang in self.languages.values()))
        # now have to make blocks of 16 consecutive IDs
        bundles = []
        while all_ids:
            first_index = min(all_ids)
            base_id = first_index // 16
            first_index = base_id * 16  # round (down) to a multiple of 16
            bundle_ids = range(first_index, first_index + 16)
            #~ print base_id, bundle_ids
            all_ids -= set(bundle_ids)
            for lang in self.languages:
                bundle_data = encode_string_table_bundle(
                    first_index,
                    [self.languages[lang].get(n, u'') for n in bundle_ids])
                #~ print repr(bundle_data)
                res.update(RT_STRING, base_id + 1, lang, bundle_data)


class ResourceReader(object):
    """Access resources in exe and dll"""

    def __init__(self, filname):
        self.filename = filname

    def __enter__(self):
        self.hsrc = LoadLibraryEx(self.filename, 0, LOAD_LIBRARY_AS_DATAFILE)
        return self
    
    def __exit__(self, *args):
        if self.hsrc:
            ctypes.windll.kernel32.FreeLibrary(self.hsrc)
        self.hsrc = None

    def enumerate_types(self):
        types = []
        @EnumResTypeProc
        def remember_type(handle, type, param):
            types.append(type)
            return True
        EnumResourceTypes(self.hsrc, remember_type, 0)
        return types

    def enumerate_names(self, type):
        names = []
        @EnumResNameProc
        def remember_name(hModule, lpszType, lpszName, lParam):
            names.append(lpszName)
            return True
        EnumResourceNames(self.hsrc, type, remember_name, 0)
        return names

    def enumerate_languages(self, type, name):
        languages = []
        @EnumResLangProc
        def remember_languages(hModule, lpszType, lpszName, wIDLanguage, lParam):
            languages.append(wIDLanguage)
            return True
        EnumResourceLanguages(self.hsrc, type, name, remember_languages, 0)
        return languages

    def get_resource(self, type, name, lang):
        hres = FindResourceEx(self.hsrc, type, name, lang)
        r = LoadResource(self.hsrc, hres)
        size = SizeofResource(self.hsrc, hres)
        return bytearray((ctypes.c_ubyte * size).from_address(LockResource(r)))

    def make_dict(self):
        d = {}
        for type in self.enumerate_types():
            names = {}
            d[type] = names
            for name in self.enumerate_names(type):
                langs = {}
                names[name] = langs
                for lang in self.enumerate_languages(type, name):
                    langs[lang] = self.get_resource(type, name, lang)
        return d

    def get_string_table(self):
        string_table = StringTable()
        string_table.load_from_resource(self)
        return string_table


class ResourceEditor(object):
    """Access resources for editing in exe and dll"""

    def __init__(self, filname):
        self.filename = filname

    def __enter__(self):
        self.hdst = BeginUpdateResource(self.filename, False)
        return self
    
    def __exit__(self, *args):
        if self.hdst:
            EndUpdateResource(self.hdst, False)
        self.hdst = None

    def update(self, type, name, lang, data):
        if data is not None:
            UpdateResource(self.hdst, type, name, lang,
                           (ctypes.c_ubyte * len(data)).from_buffer_copy(data),
                           len(data))
        else:
            UpdateResource(self.hdst, type, name, lang, None, 0)  # deletes entry

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def action_dump(args):
    with ResourceReader(args.FILE) as res:
        d = res.make_dict()
        pprint(d)


def action_edit(args):
    with ResourceEditor(args.FILE) as res:
        for removal in args.delete:
            type, name, lang = removal.split(':')
            res.update(int(type), int(name), int(lang), None)
        for addition in args.add:
            type, name, lang, data = addition.split(':')
            res.update(int(type), int(name), int(lang), data)


def action_dump_strings(args):
    with ResourceReader(args.FILE) as res:
        string_table = res.get_string_table()
        for language, strings in sorted(string_table.languages.items()):
            sys.stdout.write('== language: {}\n'.format(language))
            for n, s in sorted(strings.items()):
                sys.stdout.write('{}: {}\n'.format(n, s))


def action_edit_strings(args):
    with ResourceReader(args.FILE) as res:
        string_table = res.get_string_table()
    for change in args.set:
        id, text = change.split(':', 1)
        string_table.languages[args.lang][int(id)] = text
    #~ pprint(string_table.languages)
    with ResourceEditor(args.FILE) as res:
        string_table.save_to_resource(res)


def main():
    parser = argparse.ArgumentParser(description='Windows Resource Editor')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_dump = subparsers.add_parser('dump', help='Read and output resources.')
    parser_dump.add_argument('FILE', help='File to read from (.exe, .dll)')
    parser_dump.set_defaults(func=action_dump)

    parser_edit = subparsers.add_parser('edit', help='Edit resources.')
    parser_edit.add_argument('FILE', help='File to edit (.exe, .dll)')
    parser_edit.add_argument('--add', action='append', default=[], help='add specified resource')
    parser_edit.add_argument('--delete', action='append', default=[], help='remove resources')
    parser_edit.set_defaults(func=action_edit)

    parser_dump_strings = subparsers.add_parser('dump_strings', help='Read and output string table resource.')
    parser_dump_strings.add_argument('FILE', help='File to read from (.exe, .dll)')
    parser_dump_strings.set_defaults(func=action_dump_strings)

    parser_edit_strings = subparsers.add_parser('edit_strings', help='Edit resources.')
    parser_edit_strings.add_argument('FILE', help='File to edit (.exe, .dll)')
    parser_edit_strings.add_argument('--set', action='append', default=[], help='(over)write specified text')
    parser_edit_strings.add_argument('--lang', type=int, default=1033, help='language ID')
    parser_edit_strings.set_defaults(func=action_edit_strings)

    args = parser.parse_args()
    args.func(args)  # calls the subcommand, see func attributes above

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
