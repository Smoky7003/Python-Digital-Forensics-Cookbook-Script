###########################################
from __future__ import print_function
import os
import sys
import pytz
import glob
import shutil
import argparse
from pywintypes import Time
from datetime import datetime as dt
from win32file import GENERIC_WRITE, FILE_SHARE_WRITE
from win32file import SetFileTime, CreateFile, CloseHandle
from win32file import OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL
###########################################
__authors__ = ["Oldked"]
__description__ = 'My python toolkit Script'
__version__ = "v0.1"
###########################################
parser = argparse.ArgumentParser(description=__description__, epilog="Developed by {}".format(", ".join(__authors__)))
parser.add_argument("--scan", help="Scan a directory",action='store_true')
parser.add_argument("--metadata", help="Analyze a file metadata",action='store_true')
parser.add_argument("--copy-metadata", help="Copy a file without changing metadata (WINDOWS ONLY)",action='store_true')
parser.add_argument("--path","-p", help="Path to a file or directory", required=False)
parser.add_argument("--output", help="Path to output file")
parser.add_argument("--extension", help="search files with a specific extension")
parser.add_argument("--version", help="Displays script version information",action="version", version=str(__version__))
parser.add_argument("--timezone", help="Timezone of the file's timestamp", choices=['EST5EDT', 'CST6CDT', 'MST7MDT', 'PST8PDT'])

args = parser.parse_args()
output = args.output
path = args.path
extension = args.extension
########################################### python .\test.py --timezone EST5EDT .\README.md .\TEST\
#Scan via un dossier
if args.scan and not args.extension:
    files = glob.glob("{}/**".format(path), recursive = True)
    for file in files:
	    print(file)
#Scan via une extension
if args.scan and args.extension:
    files = glob.glob("{}/**/*.{}".format(path, extension), recursive = True)
    for file in files:
	    print(file)
#Scan des metadata d'un fichier
if args.metadata and args.path:
    stat_info = os.stat(path)
    if "linux" in sys.platform or "darwin" in sys.platform:
        print("Change time: ", dt.fromtimestamp(stat_info.st_ctime))
    elif "win" in sys.platform:
        print("Creation time: ", dt.fromtimestamp(stat_info.st_ctime))
    else:
        print("[-] Unsupported platform {} detected. Cannot interpret "
            "creation/change timestamp.".format(sys.platform)
            )
    print("Modification time: ", dt.fromtimestamp(stat_info.st_mtime))
    print("Access time: ", dt.fromtimestamp(stat_info.st_atime))
    print("File mode: ", stat_info.st_mode)
    print("File inode: ", stat_info.st_ino)
    major = os.major(stat_info.st_dev)
    minor = os.minor(stat_info.st_dev)
    print("Device ID: ", stat_info.st_dev)
    print("\tMajor: ", major)
    print("\tMinor: ", minor)
    print("Number of hard links: ", stat_info.st_nlink)
    print("Owner User ID: ", stat_info.st_uid)
    print("Group ID: ", stat_info.st_gid)
    print("File Size: ", stat_info.st_size)
    print("Is a symlink: ", os.path.islink(path))
    print("Absolute Path: ", os.path.abspath(path))
    print("File exists: ", os.path.exists(path))
    print("Parent directory: ", os.path.dirname(path))
    print("Parent directory: {} | File name: {}".format(
        *os.path.split(path)))
#Copie un fichier sans altérer ses metadonnées 
if args.copy_metadata and args.path and args.timezone and args.output:
    abspath = os.path.abspath(args.path)
    if os.sep in args.path:
        src_file_name = args.path.split(os.sep, 1)[1]
    else:
        src_file_name = args.path
    output = os.path.abspath(args.output)
    tz = pytz.timezone(args.timezone)
    shutil.copy2(abspath, output)
    if os.path.isdir(output):
        dest_file = os.path.join(output, src_file_name)
    else:
        dest_file = output
    created = dt.fromtimestamp(os.path.getctime(abspath))
    created = Time(tz.localize(created))
    modified = dt.fromtimestamp(os.path.getmtime(abspath))
    modified = Time(tz.localize(modified))
    accessed = dt.fromtimestamp(os.path.getatime(abspath))
    accessed = Time(tz.localize(accessed))
    print("Source\n======")
    print("Created:  {}\nModified: {}\nAccessed: {}".format(
        created, modified, accessed))
    handle = CreateFile(dest_file, GENERIC_WRITE, FILE_SHARE_WRITE,
                        None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
    SetFileTime(handle, created, accessed, modified)
    CloseHandle(handle)
    created = tz.localize(dt.fromtimestamp(os.path.getctime(dest_file)))
    modified = tz.localize(dt.fromtimestamp(os.path.getmtime(dest_file)))
    accessed = tz.localize(dt.fromtimestamp(os.path.getatime(dest_file)))
    print("\nDestination\n===========")
    print("Created:  {}\nModified: {}\nAccessed: {}".format(
        created, modified, accessed))
else : 
     parser.error('--copy-metadata requires --timezone, --path, and --output')
