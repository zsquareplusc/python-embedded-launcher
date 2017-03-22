=====
 API
=====

Launcher
========
A small helper module called ``launcher`` is automatically packaged with the
exe. It contains a few helper functions.

.. module:: launcher

.. function:: patch_sys_path()

    Add directories (relative to executable, if existing) to ``sys.path``.

    - the directory of the executable
    - ``Python{py.major}{py.minor}/site-packages``
    - ``Python{py.major}{py.minor}/Lib/site-packages``
    - ``Lib/site-packages``

    These locations are also scanned for ``.pth`` files.

    This function is called automatically by the start code.


.. function:: extend_sys_path_by_pattern(pattern)

    :param str pattern: String with wildcard

    Add files matching a pattern (e.g. ``*.zip``, ``*.whl``, ``*.egg``) to
    ``sys.path``. The pattern is prefixed with the location of the executable.
    In case of wheel files, it only works for pure Python wheels and only if
    they do no access the file system to load data on their own (should use
    pkgutil_). This function is used if the command line option
    ``--extend-sys-path`` is used.


.. function :: restore_sys_argv()

    Get original command line via Windows API. Restores ``sys.argv`` (which is
    used by the launcher to pass the location of Python). This function is
    called by the default boot code (``__main__``).

    Note: Python 2 usually has ``str`` elements in ``sys.argv``, but this
    function sets them to be ``unicode``.


.. function:: close_console()

    Useful for GUI applications, it closes a separate console window if there
    is one, e.g. when the exe was started by a double click. It is safe to
    call this function even if the application was started in a console
    (determined with :func:`is_separate_console_window()`)

    Note that ``sys.stdout``, ``sys.stderr`` and ``sys.stdin`` are replaced
    with a dummy objects that ignore ``write()``/``flush()`` and return
    empty strings on ``read()``.

    Note: some functions may access the std streams, bypassing ``sys.stdXXX```,
    those will fail due to the closed steams.


.. function:: is_separate_console_window()

    :return: true if the process has a console

    Return true if the console window was opened with this process (e.g.
    the console was opened because the exe was started from the file Explorer).


.. function:: hide_console(hide=True)

    :param bool hide: Hide console when true, show it when false

    Hides the console window, if one was opened for the process. The function
    can also be called to show the window again. This function is used
    by ``hide_console_until_error()``


.. function:: hide_console_until_error()

    Hides the console window, if one was opened for the process, but shows the
    console window again when a traceback is printed. ``sys.excepthook`` is
    set by this function and it calls the previous value after showing the
    console window again.


.. function:: wait_at_exit()

    Wait at exit, but only if console window was opened separately. So if
    the application was started in a console, there is no extra waiting, while
    when it was started from the GUI and a separate console window is opended,
    it will wait extra, so that the user can read the output.

    This function is called automatically if the command line option
    ``--wait`` is used.


.. function:: wait_on_error()

    Wait if the program terminates with an exception, but only if console
    window was opened separately.

    This function is called automatically if the command line option
    ``--wait-on-error`` is used.

.. _pkgutil: https://docs.python.org/3/library/pkgutil.html


Launcher Package
================
The launcher tools can not only be used as scripts but also as Python
libraries.


``download_python3_minimal``
----------------------------
.. module:: launcher_tool.download_python3_minimal

.. function:: get_url(version, bits)

    :param str version: Version specification, such as '3.5.2' or '3.6'
    :param int bits: 32 or 64

    Calculate download URL for Python embed distribution, based on version
    and architecture.


.. function:: extract(url, destination, force_download=False)

    :param str url: download URL
    :param str destination: destination directory
    :param bool force_download: download even if a file is cached

    Extract ZIP file from cache, download if needed.
    e.g. ``extract(URL_32, 'python3-minimal')``


``create_python27_minimal``
---------------------------

.. module:: launcher_tool.create_python27_minimal

.. function:: copy_python(destination)

    :param str destination: destination directory

    Make a copy of Python 2.7. Including standard library (as zip) excluding
    tcl/tk, tests and site-packages. The Python files in the standard library
    are compiled. ``site-packages`` are skipped.


``copy_launcher``
-----------------

.. module:: launcher_tool.copy_launcher

.. function:: copy_launcher(fileobj, use_py2=False, use_64bits=False)

    :param filelike fileobj: a writable filelike object
    :param bool use_py2: Use Python 2.7 when true, else use Python 3.x
    :param bool use_64bits: Use 64 bit binary when true, else use 32 bit

    Copy selected variant of raw launcher exe to given file object.


``launcher_zip``
----------------

.. module:: launcher_tool.launcher_zip

.. function:: make_main(entry_point=None, run_path=None, run_module=None, \
              extend_sys_path=(), wait_at_exit=False, wait_on_error=False, \
              use_bin_dir=False, main_script=DEFAULT_MAIN)

    :param str entry_point: entry point name (optional)
    :param str run_path: script name (optional)
    :param str run_module: module name (optional)
    :param list extend_sys_path: list of paths/patterns
    :param bool wait_at_exit: add code to wait at exit
    :param bool wait_on_error: add code to wait on error
    :param str main_script: alternative to main script template
    :return: code for ``__main__.py``
    
    Generate code for ``__main__.py``. The arguments represent different
    options to start an application, handle ``sys.path`` and exit options,
    which influence the code that is generated.

    Only one of ``entry_point``, ``run_module`` and ``run_path`` should be
    used.


``resource_editor``
-------------------

.. module:: launcher_tool.resource_editor

.. class:: ResourceReader

    Read resources from a file.

    .. method:: __init__(filename)

        :param str filename: Filename of EXE to open.
    
    .. method:: enumerate_types()

        :return: a list of resource types in the file

    .. method:: enumerate_names(res_type)
        
        :return: a list of resource names (actually numbers) for given
                 resource type in the file.

    .. method:: enumerate_languages(res_type, res_name)
        
        :param int res_type: resource type
        :param int res_name: resource name
        :return: a list of language ID's for given resource name and type in
                 the file.

    .. method:: get_resource(res_type, res_name, res_lang)

        :param int res_type: resource type
        :param int res_name: resource name
        :param int res_lang: language code
        :return: resource as binary blob (bytes)

    .. method:: list_resources()

        :return: Get a flat list of resources in the file

    .. method:: make_dict()

        :return: Convert all resource entries to a dictionary and return that

    .. method:: get_string_table()

        :return: Get a decoded string table

    Can be used as context manager:

    .. method:: __enter__()

        :return: self

        Load the resources. e.g.

        >>> with ResourceReader('xy.exe') as res:
        ...     print(res.list_resources())

    .. method:: __exit__()

        Closes the file.



.. class:: ResourceEditor

    Access resources for editing in EXE and DLL.

    .. method __init__(filename)

        :param str filename: Filename of exe to open.

    .. method:: update(res_type, res_name, res_lang, data)

        :param int res_type: resource type
        :param int res_name: resource name
        :param int res_lang: language code
        :param bytes data: resource as binary blob (bytes) or ``None`` to delete

        Write (add, modify or delete) a resource entry.
        Delete entry if data is ``None``.

    Can be used as context manager:

    .. method:: __enter__()

        :return: self

        Load the resources. e.g.

        >>> with ResourceEditor('xy.exe') as res:
        ...     res.update(int(res_type), int(res_name), int(res_lang), data)

    .. method:: __exit__()

        Closes the file.


``icon``
--------

.. module:: launcher_tool.icon

Windows ICO file load/save to .ico file and resource file (.exe, .dll).

.. class:: Icon

    .. function:: clear()

        Erase current icon data.

    .. function:: load(filename)

        :param str filename: Filename to load

        Load icon from file.

    .. function:: save(filename)

        :param str filename: Filename to write to
        
        Save icon to file.

    .. function:: load_from_resource(res, res_name, res_lang=1033)

        :param ResourceReader res: resource
        :param int res_name: resource name
        :param int res_lang: language code

        Load icon from resource.

        >>> ico = icon.Icon()
        >>> with ResourceReader(args.FILE) as res:
        ...     ico.load_from_resource(res, args.name, args.lang)
        >>> ico.save(args.output)

    .. function:: save_as_resource(res, res_name, res_lang=1033)

        :param ResourceEditor res: resource
        :param int res_name: resource name
        :param int res_lang: language code
        
        Store icon as resource.

        >>> ico = icon.Icon()
        >>> ico.load(args.ICON)
        >>> with ResourceEditor(args.FILE) as res:
        ...     ico.save_as_resource(res, args.name, args.lang)
