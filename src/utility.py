import sys, os
import datetime as dt
import glob
import yaml
from pathlib import Path


def readYAML(INFILE):
    FILE_DIR = str(Path(INFILE))
    print(INFILE)
    with open(INFILE) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    for key, value in data.items():
        print(f"{key}: {value}")

    return data


def AdaptPATH(path):
    if sys.platform.startswith("linux"):
        path = path.replace("t:", "/mnt/WNTechnik").replace("\\", "/")
    elif sys.platform == "win32":
        path = path.replace("/mnt/WNTechnik", "t:").replace("/", "\\")
    return path


def ConstructFileName(PRJNUMBER, PRJNAME, WNFILETYPE, PRJREVISION, PRJDATE, FILEENDING):
    FILENAME = (
        PRJNUMBER
        + "_"
        + PRJNAME
        + "_"
        + WNFILETYPE
        + "_"
        + PRJREVISION
        + "_"
        + PRJDATE
        + FILEENDING
    )
    return FILENAME


def ConstructFileNameWithPath(
    PATH, PRJNUMBER, PRJNAME, WNFILETYPE, PRJREVISION, PRJDATE, FILEENDING
):
    FILENAME = (
        PATH
        + os.sep
        + PRJNUMBER
        + "_"
        + PRJNAME
        + "_"
        + WNFILETYPE
        + "_"
        + PRJREVISION
        + "_"
        + PRJDATE
        + FILEENDING
    )
    return FILENAME


def ExportDate():
    now = dt.datetime.now()
    # print now.strftime('%Y-%m-%d_%H%M%S')
    date = now.strftime("%Y%m%d")[2:]
    # time =  now.strftime('%H:%M:%S')
    # date =  now.strftime('%d.%m.%Y')
    # print(date)
    export = date
    return export


def today():
    import datetime

    return datetime.datetime.today().strftime("%y%m%d")


def ExportDateTime():
    now = dt.datetime.now()
    # print now.strftime('%Y-%m-%d_%H%M%S')
    atime = now.strftime("%Y.%m.%d")

    time = now.strftime("%H:%M:%S")
    # date =  now.strftime('%d.%m.%Y')
    export = atime + ", " + time
    return export


def ExportTimeBladed():
    new_format = "%d-%m-%Y@%H:%M:%S"  # 19-11-2013@15:46:22
    now = dt.datetime.now()
    export = now.strftime(new_format)
    return export


def Find_latest_file_version(directory, file):
    cwd = os.getcwd()
    os.chdir(directory)
    TargetDirectory = os.getcwd()
    file_list = []
    for file in glob.glob("*" + file + "*"):
        file_list.append(file)
    if not file_list:
        raise Exception(
            "Warning, no file named %s could be found in directory %s"
            % (file, directory)
        )
    file_list.sort()
    os.chdir(cwd)
    return TargetDirectory + "\\" + file_list[-1]


ExportDate()
