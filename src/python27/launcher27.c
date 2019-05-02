// This file is part of https://github.com/zsquareplusc/python-embedded-launcher
// (C) 2016 Chris Liechti <cliechti@gmx.net>
//
// SPDX-License-Identifier:    BSD-3-Clause
#include <windows.h>
#include <stdio.h>
#include <shellapi.h>
#include <stdbool.h>
#include <Python.h>
#include "launcher27.h"

#define FIND_FUNCTION(name) \
    FARPROC name = GetProcAddress(python_dll, #name); \
    if (name == NULL) { \
        printf(#name " not found"); \
        show_message_from_resource(IDS_PYDLL_ERROR); \
        return 1; \
    }

#define FIND_INT(name) \
    int * name = (int *)GetProcAddress(python_dll, #name); \
    if (name == NULL) { \
        printf(#name " not found"); \
        show_message_from_resource(IDS_PYDLL_ERROR); \
        return 1; \
    }

char pythonhome_relative[PATH_MAX];
char pythonhome_absolute[PATH_MAX];


// show a message dialog with text from the built-in resource
void show_message_from_resource(int id) {
    wchar_t name[80];
    wchar_t message[1024];
    LoadStringW(NULL, IDS_NAME, name, sizeof(name));
    LoadStringW(NULL, id, message, sizeof(message));
    MessageBoxW(NULL, message, name, MB_OK | MB_ICONSTOP);
}


// test if a file has a zip appended to it
bool test_zip_file(const char *path) {
    HANDLE hFile = CreateFile(path, GENERIC_READ, 0, NULL, OPEN_EXISTING, 
                              FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile != INVALID_HANDLE_VALUE) {
        char zipid[22];
        DWORD len;
        SetFilePointer(hFile, -(LONG)sizeof(zipid), NULL, FILE_END);
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
void cut_away_filename(char * path) {
    unsigned slash = 0;
    // search the entire string and remember position of last path separator
    for (unsigned pos=0; path[pos]; pos++) {
        if (path[pos] == '\\' || path[pos] == '/') {
            slash = pos;
        }
    }
    path[slash] = '\0';
}

// append a filename to a path
// does not seem that Windows has this as a function in its core, just in
// extra DLLs.
void append_filename(char *path_out, size_t outsize, const char *path_in, const char *filename) {
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
    if (outsize) *path_out = '\0';
}


bool check_if_directory_exists(char * path) {
    DWORD dwAttrib = GetFileAttributes(path);
    return (dwAttrib != INVALID_FILE_ATTRIBUTES && 
           (dwAttrib & FILE_ATTRIBUTE_DIRECTORY));
}


// set an environment variable "SELF" pointing to the location of the executable
void set_self_env(void) {
    static char env_self[PATH_MAX];
    GetModuleFileName(NULL, env_self, sizeof(env_self));
    cut_away_filename(env_self);
    SetEnvironmentVariable("SELF", env_self);
}


// where to find our python?
void get_pythonhome(void) {
    char pythonhome_in[PATH_MAX];
    LoadString(NULL, IDS_PYTHONHOME, pythonhome_in, sizeof(pythonhome_in));
    ExpandEnvironmentStrings(pythonhome_in, pythonhome_relative, sizeof(pythonhome_relative));
    GetFullPathName(pythonhome_relative, sizeof(pythonhome_absolute), pythonhome_absolute, NULL);
    //~ printf("env: %s\n", pythonhome_absolute);
}


// prefix PATH environment variable with the location of our Python installation
void patch_path_env(void) {
    static char env_path[32760];
    unsigned pos = snprintf(env_path, sizeof(env_path), "%s;", pythonhome_absolute);
    GetEnvironmentVariable("PATH", &env_path[pos], sizeof(env_path) - pos);
    SetEnvironmentVariable("PATH", env_path);
}


int main() {
    set_self_env();
    get_pythonhome();
    if (!check_if_directory_exists(pythonhome_absolute)) {
        printf("ERROR python minimal distribution not found!\n"
               "Directory not found: %s\n", pythonhome_absolute);
        show_message_from_resource(IDS_PY_NOT_FOUND);
        return 3;
    }
    // patch PATH so that DLLs can be found
    patch_path_env();

    char pydll_path[PATH_MAX];
    append_filename(pydll_path, sizeof(pydll_path), pythonhome_absolute, "python27.dll");
    HMODULE python_dll = LoadLibrary(pydll_path);
    if (python_dll == NULL) {
        printf("Python is expected in: %s\n\n"
               "ERROR Python DLL not found!\n"
               "File not found: %s\n" , pythonhome_absolute, pydll_path);
        show_message_from_resource(IDS_PYDLL_NOT_FOUND);
        return 1;
    }

    // get a few pointers to symbols in Python DLL
    FIND_FUNCTION(Py_Main)
    FIND_FUNCTION(Py_SetProgramName)
    FIND_FUNCTION(Py_SetPythonHome)
    FIND_FUNCTION(Py_Initialize)
    FIND_FUNCTION(PySys_SetPath)
    FIND_INT(Py_IgnoreEnvironmentFlag)
    FIND_INT(Py_NoSiteFlag)
    FIND_INT(Py_NoUserSiteDirectory)
    FIND_INT(Py_DontWriteBytecodeFlag)

    // Set the name and isolate Python from the environment
    char argv_0[PATH_MAX];
    GetModuleFileName(NULL, argv_0, sizeof(argv_0));
    Py_SetProgramName(argv_0);
    Py_SetPythonHome(pythonhome_absolute);
    *Py_NoUserSiteDirectory = 1;
    *Py_IgnoreEnvironmentFlag = 1;
    *Py_DontWriteBytecodeFlag = 1;
    *Py_NoSiteFlag = 1;
    // must ensure that python finds its "landmark file" Lib/os.py (it is in our python27.zip)
    // Python 2.7 lacks the handy Py_SetPath function (available in 3.x only)
    // so we have to call Py_Initialize and override sys.path afterwards
    Py_Initialize();
    char pythonpath[32768];
    snprintf(pythonpath, sizeof(pythonpath), "%s;%s\\python27.zip", pythonhome_absolute, pythonhome_absolute);
    PySys_SetPath(pythonpath);

    // the application is appended as zip to the exe. so load ourselfes
    // to get a nice user feedback, test first if the zip is really appended
    if (!test_zip_file(argv_0)) {
        printf("ERROR application not found!\n"
               "No zip data appended to file: %s\n", argv_0);
        show_message_from_resource(IDS_ZIP_NOT_FOUND);
        return 1;
    }

    // use the high level entry to start our boot code, pass along the location of our python installation
    int retcode = Py_Main(3, (char *[]){"", argv_0, pythonhome_absolute});
    //~ printf("exitcode %d\n", retcode);
    return retcode;
}

