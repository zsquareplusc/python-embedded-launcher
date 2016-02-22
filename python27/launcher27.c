#include <windows.h>
#include <stdio.h>
#include <shellapi.h>
#include <stdbool.h>
#include <Python.h>

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

#define IDS_NAME                1
#define IDS_PYTHONHOME          2
#define IDS_PY_NOT_FOUND        3
#define IDS_PYDLL_NOT_FOUND     4
#define IDS_PYDLL_ERROR         5
#define IDS_ZIP_NOT_FOUND       6

// show a message dialog with text from the built-in resource
void show_message_from_resource(int id) {
    char name[80];
    char message[1024];
    LoadString(NULL, IDS_NAME, name, sizeof(name));
    LoadString(NULL, id, message, sizeof(message));
    MessageBox(NULL, message, name, MB_OK | MB_ICONSTOP);
}


// test if a file has a zip appended to it
bool test_zip_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (f != NULL) {
        char zipid[22];
        fseek(f, -sizeof(zipid), 2);
        fread(zipid, 1, sizeof(zipid), f);
        fclose(f);
        //~ printf("zipid: %s\n", zipid);
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


int main(int argc, char *argv[]) {
    // where to find our python? read path from resource and check if it exitsts
    char pythonhome_in[PATH_MAX];
    char pythonhome[PATH_MAX];
    // set an environment variable pointing to the location of the executable
    char env_self[PATH_MAX+5] = "SELF=";
    GetModuleFileName(NULL, &env_self[5], sizeof(env_self)-5);
    cut_away_filename(env_self);
    putenv(env_self);

    LoadString(NULL, IDS_PYTHONHOME, pythonhome_in, sizeof(pythonhome_in));
    ExpandEnvironmentStrings(pythonhome_in, pythonhome, sizeof(pythonhome));
    struct stat st;
    if (0 > stat(pythonhome, &st)) {
        printf("ERROR python minimal distribution not found!\ndirectory not found: %s\n", pythonhome);
        show_message_from_resource(IDS_PY_NOT_FOUND);
        return 3;
    }

    // patch PATH so that DLL can be found
    char pyminimal_path[PATH_MAX];
    char env_path[32768];
    char argv_0[PATH_MAX];
    GetFullPathName(pythonhome, sizeof(pyminimal_path), pyminimal_path, NULL);
    //~ printf("env: %s\n", pyminimal_path);
    snprintf(env_path, sizeof(env_path), "PATH=%s;%s", pyminimal_path, getenv("PATH"));
    putenv(env_path);
    //~ printf("env: %s\n", env_path);
    //~ printf("argv_0: %s\n", argv_0);

    // load the python DLL
    HMODULE python_dll = LoadLibrary("python27.dll");
    if (python_dll == NULL) {
        printf("ERROR Python DLL not found!\nfile not found: python27.dll\n");
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
    char name[80];
    LoadString(NULL, IDS_NAME, name, sizeof(name));
    Py_SetProgramName(name);
    Py_SetPythonHome(pyminimal_path);
    *Py_NoUserSiteDirectory = 1;
    *Py_IgnoreEnvironmentFlag = 1;
    *Py_DontWriteBytecodeFlag = 1;
    *Py_NoSiteFlag = 1;
    // must ensure that python finds its "landmark file" Lib/os.py (it is in our python27.zip)
    Py_Initialize();
    char pythonpath[32768];
    snprintf(pythonpath, sizeof(pythonpath), "%s;%s\\python27.zip", pyminimal_path, pyminimal_path);
    PySys_SetPath(pythonpath);

    // the application is appended as zip to the exe. so load ourselfes
    // fix filename as windows does not always tell the truth (PATHEXT stuff)
    GetFullPathName(argv[0], sizeof(argv_0), argv_0, NULL);
    int len = strlen(argv_0);
    // append .exe if it is missing
    if (strcasecmp(&argv_0[len-4], ".exe")) {
        strncat(argv_0, ".exe", sizeof(argv_0));
    }

    // to get a nice user feedback, test first if the zip is really appended
    if (!test_zip_file(argv_0)) {
        printf("ERROR application not found!\nno zip data appended to file: %s\n", argv_0);
        show_message_from_resource(IDS_ZIP_NOT_FOUND);
        return 1;
    }

    // use the high level entry to start our boot code, pass along the location of our python installation
    int retcode = Py_Main(3, (char *[]){"", argv_0, pyminimal_path});
    //~ int retcode = Py_Main(4, (char *[]){"", "-i", argv_0, pyminimal_path});
    //~ printf("exitcode %d\n", retcode);
    return retcode;
}

