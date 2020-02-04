#!python
#
# This file is part of https://github.com/zsquareplusc/python-embedded-launcher
# (C) 2016-2019 Chris Liechti <cliechti@gmx.net>
#
# SPDX-License-Identifier:    BSD-3-Clause
"""\
Use Windows API to change resources in exe/dll's.

This module uses the Windows API to manipulate files and therefore must
be run on Windows or a compatible system.
"""
# pylint: disable=invalid-name,line-too-long,unused-argument,missing-docstring

import argparse
import ctypes
from ctypes.wintypes import HANDLE, HMODULE, HRSRC, HGLOBAL, BOOL, LPCWSTR, WORD, DWORD
import itertools
import struct
import sys
from pprint import pprint

import launcher_tool.icon as icon

LOAD_LIBRARY_AS_DATAFILE = 2
RT_STRING = 6
RT_ICON = 3
RT_GROUP_ICON = 14

RESOURCE_TYPES = {
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

def check_null(result, function, arguments, *args):
    if result is None or result == 0:
        raise ctypes.WinError()
    return result

def ValidHandle(value):
    """Check if it is not NULL, raise WinError if it is."""
    if value == 0:
        raise ctypes.WinError()
    return value

check_bool = ValidHandle

LoadLibraryEx = ctypes.windll.kernel32.LoadLibraryExW
LoadLibraryEx.argtypes = [LPCWSTR, HANDLE, DWORD]
LoadLibraryEx.restype = HMODULE
LoadLibraryEx.errcheck = check_null

FreeLibrary = ctypes.windll.kernel32.FreeLibrary
FreeLibrary.argtypes = [HMODULE]
FreeLibrary.restype = BOOL

LoadResource = ctypes.windll.kernel32.LoadResource
LoadResource.argtypes = [HMODULE, HRSRC]  # hModule,  hResInfo
LoadResource.restype = HMODULE
LoadResource.errcheck = check_null

FindResourceEx = ctypes.windll.kernel32.FindResourceExW
#~ FindResourceEx.argtypes =  [HMODULE, LPCTSTR, LPCTSTR, WORD]  # hModule, lpType, lpName, wLanguage
FindResourceEx.argtypes = [HMODULE, ctypes.c_int, ctypes.c_int, WORD]  # hModule, lpType, lpName, wLanguage
FindResourceEx.restype = HRSRC
FindResourceEx.errcheck = check_null

SizeofResource = ctypes.windll.kernel32.SizeofResource
SizeofResource.argtypes = [HMODULE, HRSRC]  # hModule,  hResInfo
SizeofResource.restype = DWORD

LockResource = ctypes.windll.kernel32.LockResource
LockResource.argtypes = [HGLOBAL]  # hResData
LockResource.restype = ctypes.c_void_p

#~ EnumResTypeProc = ctypes.CFUNCTYPE(BOOL, HMODULE, LPTSTR, LONG_PTR) # hModule lpszType lParam
EnumResTypeProc = ctypes.CFUNCTYPE(BOOL, HMODULE, ctypes.c_int, ctypes.c_int)  # hModule lpszType lParam

EnumResourceTypes = ctypes.windll.Kernel32.EnumResourceTypesW
EnumResourceTypes.argtypes = [HMODULE, EnumResTypeProc, ctypes.c_int]  # hModule, lpEnumFunc, lParam
EnumResourceTypes.restype = check_bool


#~ EnumResNameProc = ctypes.CFUNCTYPE(BOOL, HMODULE, LPCWSTR, LPWSTR, ctypes.c_int) # hModule, lpszType, lpszName, lParam
EnumResNameProc = ctypes.CFUNCTYPE(BOOL, HMODULE, ctypes.c_int, ctypes.c_int, ctypes.c_int)  # hModule, lpszType, lpszName, lParam

EnumResourceNames = ctypes.windll.kernel32.EnumResourceNamesW
#~ EnumResourceNames.argtypes = [HMODULE, LPCWSTR, EnumResNameProc, ctypes.c_int] # hModule, lpszType, lpEnumFunc, lParam
EnumResourceNames.argtypes = [HMODULE, ctypes.c_int, EnumResNameProc, ctypes.c_int]  # hModule, lpszType, lpEnumFunc, lParam
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
UpdateResource.argtypes = [HANDLE, ctypes.c_int, ctypes.c_int, WORD, ctypes.POINTER(ctypes.c_ubyte), DWORD]  # hUpdate  lpType  lpName wLanguage lpData cbData
UpdateResource.restype = BOOL

BeginUpdateResource = ctypes.windll.kernel32.BeginUpdateResourceW
BeginUpdateResource.argtypes = [LPCWSTR, BOOL]  # pFileName  bDeleteExistingResources
BeginUpdateResource.restype = HANDLE

EndUpdateResource = ctypes.windll.kernel32.EndUpdateResourceW
EndUpdateResource.argtypes = [HANDLE, BOOL]  # hUpdate  fDiscard
EndUpdateResource.restype = BOOL

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def decode_string_table_bundle(table):
    """Decode a bundle of 16 strings from a resource"""
    (first_index,) = struct.unpack(b'<H', table[:2])
    strings = [u'' for i in range(16)]
    pos = 2
    for i in range(16):
        if pos + 1 > len(table):
            break
        (length,) = struct.unpack(b'<H', table[pos : pos + 2])
        pos += 2
        strings[i] = table[pos : pos + length * 2].decode('utf-16')
        #~ print i, table[pos :]
        pos += length * 2
    return first_index, strings


def encode_string_table_bundle(first_index, strings):
    """Encode a bundle of 16 strings for a resource"""
    if len(strings) != 16:
        raise ValueError('strings must have 16 entries')
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
        """Load and decode string table"""
        self.languages = {}
        for res_name in res.enumerate_names(RT_STRING):
            for res_lang in res.enumerate_languages(RT_STRING, res_name):
                s_id, strings = decode_string_table_bundle(
                    res.get_resource(RT_STRING, res_name, res_lang))
                d = self.languages.setdefault(res_lang, {})
                for n, s in enumerate(strings, s_id + (res_name - 1) * 16):
                    if s:
                        d[n] = s

    def save_to_resource(self, res):
        """Encode and store string table"""
        # find out which IDs are in use
        all_ids = set(n for n, text in itertools.chain.from_iterable(
            res_lang.items() for res_lang in self.languages.values()))
        # now have to make blocks of 16 consecutive IDs
        while all_ids:
            first_index = min(all_ids)
            base_id = first_index // 16
            first_index = base_id * 16  # round (down) to a multiple of 16
            bundle_ids = range(first_index, first_index + 16)
            #~ print base_id, bundle_ids
            all_ids -= set(bundle_ids)
            for res_lang in self.languages:
                bundle_data = encode_string_table_bundle(
                    first_index,
                    [self.languages[res_lang].get(n, u'') for n in bundle_ids])
                #~ print repr(bundle_data)
                res.update(RT_STRING, base_id + 1, res_lang, bundle_data)


class ResourceReader(object):
    """Access resources in exe and dll"""

    def __init__(self, filename):
        self.filename = filename
        self.hsrc = None

    def __enter__(self):
        self.hsrc = LoadLibraryEx(self.filename, 0, LOAD_LIBRARY_AS_DATAFILE)
        return self

    def __exit__(self, *args):
        if self.hsrc:
            FreeLibrary(self.hsrc)
        self.hsrc = None

    def enumerate_types(self):
        """Return a list of resource types in the file"""
        types = []

        @EnumResTypeProc
        def remember_type(handle, res_type, param):
            types.append(res_type)
            return True
        EnumResourceTypes(self.hsrc, remember_type, 0)
        return types

    def enumerate_names(self, res_type):
        """\
        Return a list of resource names (actually numbers) for given resource
        type in the file.
        """
        names = []

        @EnumResNameProc
        def remember_name(hModule, lpszType, lpszName, lParam):
            names.append(lpszName)
            return True
        EnumResourceNames(self.hsrc, res_type, remember_name, 0)
        return names

    def enumerate_languages(self, res_type, res_name):
        """\
        Return a list of language ID's for given resource
        name and type in the file.
        """
        languages = []

        @EnumResLangProc
        def remember_languages(hModule, lpszType, lpszName, wIDLanguage, lParam):
            languages.append(wIDLanguage)
            return True
        EnumResourceLanguages(self.hsrc, res_type, res_name, remember_languages, 0)
        return languages

    def get_resource(self, res_type, res_name, res_lang):
        """Read resource as binary blob"""
        hres = FindResourceEx(self.hsrc, res_type, res_name, res_lang)
        r = LoadResource(self.hsrc, hres)
        size = SizeofResource(self.hsrc, hres)
        return bytearray((ctypes.c_ubyte * size).from_address(LockResource(r)))

    def list_resources(self):
        """Get a flat list of resources in the file"""
        resources = []
        for res_type in self.enumerate_types():
            if res_type > 10000:
                continue
            for res_name in self.enumerate_names(res_type):
                if res_name > 10000:
                    continue
                for res_lang in self.enumerate_languages(res_type, res_name):
                    resources.append((res_type, res_name, res_lang))
        return resources

    def make_dict(self):
        """Convert all resource entries to a dictionary"""
        d = {}
        for res_type in self.enumerate_types():
            names = {}
            d[res_type] = names
            for res_name in self.enumerate_names(res_type):
                langs = {}
                names[res_name] = langs
                for res_lang in self.enumerate_languages(res_type, res_name):
                    langs[res_lang] = self.get_resource(res_type, res_name, res_lang)
        return d

    def get_string_table(self):
        """Get a decoded string table"""
        string_table = StringTable()
        string_table.load_from_resource(self)
        return string_table


class ResourceEditor(object):
    """Access resources for editing in exe and dll"""
    # pylint: disable=too-few-public-methods

    def __init__(self, filename):
        self.filename = filename
        self.hdst = None

    def __enter__(self):
        self.hdst = BeginUpdateResource(self.filename, False)
        return self

    def __exit__(self, *args):
        if self.hdst:
            EndUpdateResource(self.hdst, False)
        self.hdst = None

    def update(self, res_type, res_name, res_lang, data):
        """\
        Write (add, modify or delete) a resource entry.
        Delete entry if data is None.
        """
        if data is not None:
            UpdateResource(self.hdst, res_type, res_name, res_lang,
                           (ctypes.c_ubyte * len(data)).from_buffer_copy(data),
                           len(data))
        else:
            UpdateResource(self.hdst, res_type, res_name, res_lang, None, 0)  # deletes entry


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def action_dump(args):
    """Print all resources as dict"""
    with ResourceReader(args.FILE) as res:
        d = res.make_dict()
        pprint(d)


def action_list(args):
    """Print all resources as dict"""
    with ResourceReader(args.FILE) as res:
        for res_type, res_name, res_lang in sorted(res.list_resources()):
            sys.stdout.write('{}:{}:{} {}\n'.format(
                res_type, res_name, res_lang, RESOURCE_TYPES.get(res_type, '?')))


def action_export(args):
    """Export a single resource to a file"""
    with ResourceReader(args.FILE) as res:
        res_type, res_name, res_lang = args.RESOURCE.split(':')
        data = res.get_resource(int(res_type), int(res_name), int(res_lang))
        args.output.write(data)


def action_export_icon(args):
    """Export an icon from resources to a file"""
    ico = icon.Icon()
    with ResourceReader(args.FILE) as res:
        if args.name is None:
            # guess an image number
            args.name = min(res_name for res_type, res_name, res_lang in res.list_resources() if res_type == RT_GROUP_ICON)
        ico.load_from_resource(res, args.name, args.lang)
    ico.save(args.output)


def write_icon(args):
    """Update an icon resource"""
    ico = icon.Icon()
    ico.load(args.ICON)
    with ResourceEditor(args.FILE) as res:
        ico.save_as_resource(res, args.name, args.lang)


def action_edit(args):
    """Write (add or modify) or deletete resource entries"""
    with ResourceEditor(args.FILE) as res:
        for removal in args.delete:
            res_type, res_name, res_lang = removal.split(':')
            res.update(int(res_type), int(res_name), int(res_lang), None)
        for addition in args.add:
            res_type, res_name, res_lang, data = addition.split(':')
            res.update(int(res_type), int(res_name), int(res_lang), data)


def action_dump_strings(args):
    """Print a list of all strings in the resources"""
    with ResourceReader(args.FILE) as res:
        string_table = res.get_string_table()
        for language, strings in sorted(string_table.languages.items()):
            sys.stdout.write('== language: {}\n'.format(language))
            for n, s in sorted(strings.items()):
                sys.stdout.write('{}: {}\n'.format(n, s))


def action_edit_strings(args):
    """Modify individual strings in the resources"""
    with ResourceReader(args.FILE) as res:
        string_table = res.get_string_table()
    for change in args.set:
        str_id, text = change.split(':', 1)
        string_table.languages[args.lang][int(str_id)] = text
    #~ pprint(string_table.languages)
    with ResourceEditor(args.FILE) as res:
        string_table.save_to_resource(res)


def main():
    """Console application entry point"""
    if sys.version_info.major == 3:
        binary_stdout = sys.stdout.buffer
    else:
        binary_stdout = sys.stdout
    parser = argparse.ArgumentParser(description='Windows Resource Editor')
    parser.add_argument('FILE', help='file containing the resources (.exe, .dll)')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    subparsers.required = True

    parser_dump = subparsers.add_parser('dump', help='read and output resources.')
    parser_dump.set_defaults(func=action_dump)

    parser_list = subparsers.add_parser('list', help='read and output resources identifiers.')
    parser_list.set_defaults(func=action_list)

    parser_export = subparsers.add_parser('export', help='export one entry to a file.')
    parser_export.add_argument('RESOURCE', metavar='TYPE:NAME:LANG', help='identification')
    parser_export.add_argument('--output', '-o', default=binary_stdout, type=argparse.FileType('wb'), help='file to write data')
    parser_export.set_defaults(func=action_export)

    parser_export_icon = subparsers.add_parser('export_icon', help='export icon to a file.')
    parser_export_icon.add_argument('--name', type=int, help='resource ID')
    parser_export_icon.add_argument('--lang', type=int, default=1033, help='resource language')
    parser_export_icon.add_argument('--output', '-o', metavar='FILE', help='file to write data', required=True)
    parser_export_icon.set_defaults(func=action_export_icon)

    parser_write_icon = subparsers.add_parser('write_icon', help='write icon to a resource file.')
    parser_write_icon.add_argument('ICON', help='icon to read')
    parser_write_icon.add_argument('--name', type=int, default=1, help='resource ID')
    parser_write_icon.add_argument('--lang', type=int, default=1033, help='resource language')
    parser_write_icon.set_defaults(func=write_icon)

    parser_edit = subparsers.add_parser('edit', help='edit resources.')
    parser_edit.add_argument('--add', action='append', default=[], help='add specified resource')
    parser_edit.add_argument('--delete', action='append', default=[], help='remove resources')
    parser_edit.set_defaults(func=action_edit)

    parser_dump_strings = subparsers.add_parser('dump_strings', help='read and output string table resource.')
    parser_dump_strings.set_defaults(func=action_dump_strings)

    parser_edit_strings = subparsers.add_parser('edit_strings', help='edit resources.')
    parser_edit_strings.add_argument('--set', action='append', default=[], help='(over)write specified text')
    parser_edit_strings.add_argument('--lang', type=int, default=1033, help='language ID')
    parser_edit_strings.set_defaults(func=action_edit_strings)

    args = parser.parse_args()
    args.func(args)  # calls the subcommand, see func attributes above

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
