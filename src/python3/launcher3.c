// This file is part of https://github.com/zsquareplusc/python-embedded-launcher
// (C) 2016-2017 Chris Liechti <cliechti@gmx.net>
//
// SPDX-License-Identifier:    BSD-3-Clause

#include <windows.h>
#include <stdio.h>
#include <shellapi.h>
#include <stdbool.h>
#include <string.h>
#include <wchar.h>
#include "launcher3.h"

#define Py_LIMITED_API
#include <Python.h>

#define FIND_FUNCTION(name) \
    FARPROC name = GetProcAddress(python_dll, #name); \
    if (name == NULL) { \
        printf(#name " not found"); \
        show_message_from_resource(IDS_PYDLL_ERROR); \
        return 1; \
    }


#define PATH_LENGTH     PATH_MAX

wchar_t pythonhome_relative[PATH_LENGTH];
wchar_t pythonhome_absolute[PATH_LENGTH];


// show a message dialog with text from the built-in resource
void show_message_from_resource(int id) {
    wchar_t name[80];
    wchar_t message[1024];
    LoadString(NULL, IDS_NAME, name, 80);
    LoadString(NULL, id, message, 1024);
    MessageBox(NULL, message, name, MB_OK | MB_ICONSTOP);
}


// test if a file has a zip appended to it
bool test_zip_file(const wchar_t *path) {
    HANDLE hFile = CreateFile(path, GENERIC_READ, 0, NULL, OPEN_EXISTING, 
                              FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile != INVALID_HANDLE_VALUE) {
        char zipid[22];
        DWORD len;
        SetFilePointer(hFile, (LONG)(-sizeof(zipid)), NULL, FILE_END);
        ReadFile(hFile, zipid, sizeof(zipid), &len, NULL);
        CloseHandle(hFile);
        return 0 == memcmp(zipid, "PK\005\006", 4);
    } else {
        return false;
    }
}


// given a path, write a null byte where the filename starts
// does not seem that Windows has this as a function in its core, just in
// extra DLLs.
void cut_away_filename(wchar_t * path) {
    unsigned slash = 0;
    // search the entire string and remember position of last path separator
    for (unsigned pos=0; path[pos]; pos++) {
        if (path[pos] == L'\\' || path[pos] == L'/') {
            slash = pos;
        }
    }
    path[slash] = '\0';
}

// append a filename to a path
// does not seem that Windows has this as a function in its core, just in
// extra DLLs.
void append_filename(wchar_t *path_out, size_t outsize, const wchar_t *path_in,
                     const wchar_t *filename, const wchar_t *extension) {
    while (outsize && *path_in) {
        *path_out++ = *path_in++;
        outsize--;
    }
    if (outsize) {
        *path_out++ = '\\';
        outsize--;
    }
    while (outsize && *filename) {
        *path_out++ = *filename++;
        outsize--;
    }
    while (outsize && *extension) {
        *path_out++ = *extension++;
        outsize--;
    }
    if (outsize) *path_out = '\0';
}


bool check_if_directory_exists(wchar_t * path) {
    DWORD dwAttrib = GetFileAttributes(path);
    return (dwAttrib != INVALID_FILE_ATTRIBUTES && 
           (dwAttrib & FILE_ATTRIBUTE_DIRECTORY));
}


// set an environment variable "SELF" pointing to the location of the executable
void set_self_env(void) {
    static wchar_t env_self[PATH_LENGTH];
    GetModuleFileName(NULL, env_self, PATH_LENGTH);
    cut_away_filename(env_self);
    SetEnvironmentVariable(L"SELF", env_self);
}


// where to find our python?
void get_pythonhome(void) {
    wchar_t pythonhome_in[PATH_LENGTH];
    LoadString(NULL, IDS_PYTHONHOME, pythonhome_in, PATH_LENGTH);
    ExpandEnvironmentStrings(pythonhome_in, pythonhome_relative, PATH_LENGTH);
    GetFullPathName(pythonhome_relative, PATH_LENGTH, pythonhome_absolute, NULL);
    //~ wprintf(L"env: %s\n", pythonhome_absolute);
}


// prefix PATH environment variable with the location of our Python installation
void patch_path_env(void) {
    static wchar_t env_path[32768];
    unsigned pos = snwprintf(env_path, 32768, L"%s;", pythonhome_absolute);
    GetEnvironmentVariable(L"PATH", &env_path[pos], 32768 - pos);
    SetEnvironmentVariable(L"PATH", env_path);
}


// get text messages for windows error codes:
void print_last_error_message(void) {
    LPWSTR buffer;
    DWORD message_length;
    DWORD error_number = GetLastError();
    
    DWORD dwFormatFlags = FORMAT_MESSAGE_ALLOCATE_BUFFER |
        FORMAT_MESSAGE_IGNORE_INSERTS |
        FORMAT_MESSAGE_FROM_SYSTEM;
    
    message_length = FormatMessage(
        dwFormatFlags,
        NULL, // module to get message from (NULL == system)
        error_number,
        MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), // default language
        (LPWSTR) &buffer,
        0,
        NULL
    );
    if (message_length) {
        // Output message
        wprintf(L"Windows error message (Error %d):\n%s\n", error_number, buffer);
        // Free the buffer allocated by the system.
        LocalFree(buffer);
    }
}


int main() {
    set_self_env();
    get_pythonhome();
    if (!check_if_directory_exists(pythonhome_absolute)) {
        wprintf(L"ERROR python minimal distribution not found!\n"
                 "Directory not found: %s\n", pythonhome_absolute);
        show_message_from_resource(IDS_PY_NOT_FOUND);
        return 3;
    }
    // patch PATH so that DLLs can be found
    patch_path_env();

    wchar_t pydll_path[PATH_LENGTH];
    wchar_t python_version[20];
    
    // expand pattern in "python_version" string.
    // search for the zip file (only one match and we use it's name below anyway)
    // while for the DLL it would find python3.dll and python3x.dll...
    append_filename(pydll_path, PATH_LENGTH, pythonhome_absolute, L"python3*",  L".zip");
    WIN32_FIND_DATA find_data;
    HANDLE find_handle = FindFirstFile(pydll_path, &find_data);
    if (find_handle == NULL || find_handle == INVALID_HANDLE_VALUE) {
        wprintf(L"Python is expected in: %s\n\n"
                 "ERROR Python DLL not found!\n"
                 "full path: %s\n\n" , pythonhome_absolute, pydll_path);
        print_last_error_message();
        show_message_from_resource(IDS_PYDLL_NOT_FOUND);
        return 1;
    } else {
        // copy base name without extension
        for (wchar_t *s=find_data.cFileName, *d=python_version; *s && *s != L'.' && d < &python_version[20]; s++) {
            *d++ = *s;
            *d = L'\0';
        }
        FindClose(find_handle);
    }

    // XXX would like to use python3.dll but it would not find the real python dll (e.g. python36.dll ...)
    append_filename(pydll_path, PATH_LENGTH, pythonhome_absolute, python_version,  L".dll");
    HMODULE python_dll = LoadLibrary(pydll_path);
    if (python_dll == NULL) {
        wprintf(L"Python is expected in: %s\n\n"
                "ERROR Python DLL not found!\n"
                "File not found: %s\n" , pythonhome_absolute, pydll_path);
        print_last_error_message();
        show_message_from_resource(IDS_PYDLL_NOT_FOUND);
        return 1;
    }

    // get a few pointers to symbols in Python DLL
    FIND_FUNCTION(Py_Main)
    FIND_FUNCTION(Py_SetProgramName)
    FIND_FUNCTION(Py_SetPythonHome)
    FIND_FUNCTION(Py_SetPath)

    // Set the name and isolate Python from the environment
    wchar_t argv_0[PATH_LENGTH];
    GetModuleFileName(NULL, argv_0, PATH_LENGTH);
    Py_SetProgramName(argv_0);
    Py_SetPythonHome(pythonhome_absolute);
    // must ensure that python finds its "landmark file" Lib/os.py (it is in python3x.zip)
    wchar_t pythonpath[32768];
    snwprintf(pythonpath, 32768, L"%s;%s\\%s.zip", 
              pythonhome_absolute, pythonhome_absolute, python_version);
    Py_SetPath(pythonpath);

    // the application is appended as zip to the exe. so load ourselves
    // to get a nice user feedback, test first if the zip is really appended
    if (!test_zip_file(argv_0)) {
        wprintf(L"ERROR application not found!\n"
                 "No zip data appended to file: %s\n", argv_0);
        show_message_from_resource(IDS_ZIP_NOT_FOUND);
        return 1;
    }

    // use the high level entry to start our boot code, pass along the location of our python installation
    int retcode = Py_Main(4, (wchar_t *[]){L"", L"-I", argv_0, pythonhome_absolute});
    //~ printf("exitcode %d\n", retcode);
    return retcode;
}

