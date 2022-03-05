import os
import sys


HAS_PWD = True
try:
    import pwd
except ImportError:
    HAS_PWD = False

platform = sys.platform
if os.name == 'nt':
    platform = 'win'
if platform == 'linux2':
    platform = 'linux'

def unixpath(d):
    "unix path"
    return d.replace('\\', '/')

def winpath(d):
    "ensure path uses windows delimiters"
    if d.startswith('//'):
        d = d[1:]
    d = d.replace('/', '\\')
    return d

nativepath = unixpath
if platform == 'win':
    nativepath = winpath


def get_homedir():
    "determine home directory of current user"
    home = None
    def check(method, s):
        "check that os.path.expanduser / expandvars gives a useful result"
        try:
            if method(s) not in (None, s):
                return method(s)
        except:
            pass
        return None

    # for Unixes, allow for sudo case
    susername = os.environ.get("SUDO_USER", None)
    if home is None and HAS_PWD and susername is not None:
        home = pwd.getpwnam(susername).pw_dir

    # try expanding '~' -- should work on most Unixes
    if home is None:
        home = check(os.path.expanduser, '~')


    # try the common environmental variables
    if home is  None:
        for var in ('$HOME', '$HOMEPATH', '$USERPROFILE', '$ALLUSERSPROFILE'):
            home = check(os.path.expandvars, var)
            if home is not None:
                break

    # For Windows, ask for parent of Roaming 'Application Data' directory
    if home is None and platform == 'win':
        try:
            from win32com.shell import shellcon, shell
            home = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        except ImportError:
            pass

    # finally, use current folder
    if home is None:
        home = os.path.abspath('.')
    return nativepath(home)

def get_cwd():
    """get current working directory
    Note: os.getcwd() can fail with permission error.

    when that happens, this changes to the users `HOME` directory
    and returns that directory so that it always returns an existing
    and readable directory.
    """
    try:
        return os.getcwd()
    except:
        home = get_homedir()
        os.chdir(home)
        return home

def get_configfile(configfile):
    """get configuration file from home dir"""
    cfile = os.path.join(get_homedir(), configfile)
    if os.path.exists(cfile):
        return cfile

def save_configfile(configfile, text):
    """save text to configuration file in home dir"""
    cfile = os.path.join(get_homedir(), configfile)
    with open(cfile, 'w') as fh:
        fh.write(text)
