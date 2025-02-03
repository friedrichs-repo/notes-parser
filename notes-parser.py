import sys
import json
import os
from sty import fg, Style, RgbFg, ef, rs
import datetime
import subprocess

fg.customred = Style(RgbFg(189, 55, 55))
fg.customblue = Style(RgbFg(73, 96, 156))
fg.customgreen = Style(RgbFg(73, 156, 96))

path = os.environ['HOME'] + '/Nextcloud/physik/PHD/python/handwritten_notes/'
notes_path = os.environ['HOME'] + '/Nextcloud/epaper_notes/'
docs_path = os.environ['HOME'] + '/.parser_files/'
if os.path.isdir(docs_path) == False:
    subprocess.run(["mkdir", docs_path])


def find(keyword):
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    results = {}
    for key in dic:
        if keyword.lower() in ''.join(dic[key]).lower():
            results[key[6:10] + key[3:5] + key[:2]] = dic[key]
    if len(results):
        for key_sort in sorted(results):
            print(fg.customred + 'day:' + fg.rs, fg.customblue + key_sort[6:8] + '_' + key_sort[4:6] +
                  '_' + key_sort[:4] + fg.rs, fg.customred + 'keywords:' + fg.rs, f" {fg.customgreen}❚{fg.rs} ".join(results[key_sort]))
    else:
        print(fg.customred + 'no match for keyword' + fg.rs)


def show(*args, **kwargs):
    start = kwargs.get('start', '0')
    end = kwargs.get('end', '9')
    if len(start) > 1:
        start = start[6:10] + start[3:5] + start[:2]
    if len(end) > 1:
        end = end[6:10] + end[3:5] + end[:2]
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    dic_sort = {}
    for key in dic:
        dic_sort[key[6:10] + key[3:5] + key[:2]] = dic[key]
    for key_sort in sorted(dic_sort):
        if key_sort >= start and key_sort <= end:
            print(fg.customblue + key_sort[6:8] + '_' + key_sort[4:6] + '_' + key_sort[:4] + fg.rs,
                  f" {fg.customgreen}❚{fg.rs} ".join(dic_sort[key_sort]) + fg.rs)


def add(date, keywords):
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    if not date in dic:
        dic[date] = keywords
        with open(path + 'dic', 'w') as f:
            f.write(json.dumps(dic))
    else:
        print(fg.customred + 'entry for ' + date + ' already exists' + fg.rs)


def addto(date, keywords):
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    dic[date] += keywords
    with open(path + 'dic', 'w') as f:
        f.write(json.dumps(dic))


def remove(date):
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    try:
        del dic[date]
        with open(path + 'dic', 'w') as f:
            f.write(json.dumps(dic))
    except BaseException:
        print(date, 'does not exist')


def first():
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    dic_sort = {}
    for key in dic:
        dic_sort[key[6:10] + key[3:5] + key[:2]] = dic[key]
    date = list(sorted(dic_sort))[0]
    print(fg.customred + 'first date: ' + fg.customblue +
          date[6:8] + '_' + date[4:6] + '_' + date[:4] + fg.rs)


def last():
    with open(path + 'dic', 'r') as f:
        dic = eval(f.read())
    dic_sort = {}
    for key in dic:
        dic_sort[key[6:10] + key[3:5] + key[:2]] = dic[key]
    date = list(sorted(dic_sort))[-1]
    print(fg.customred + 'last date: ' + fg.customblue +
          date[6:8] + '_' + date[4:6] + '_' + date[:4] + fg.rs)


def read(start, end):
    start_y, start_m, start_d = start[6:10], start[3:5], start[:2]
    end_y, end_m, end_d = end[6:10], end[3:5], end[:2]

    dirs = subprocess.check_output("ls -d " + notes_path + "*/",
                                   shell=True, text=True).splitlines()

    files_to_cat = []

    for directory in dirs:
        base = directory.split("/")[-2]
        if base[:5] == "Notes":
            year = base[6:10]
            month = base[11:13]

            directory_in_window = (
                (start_y < year < end_y) or
                (year == start_y and month >= start_m and year < end_y) or
                (year == end_y and month <= end_m and year > start_y) or
                (year == start_y == end_y and start_m <= month <= end_m)
            )

            if directory_in_window:
                files = subprocess.check_output("ls " + directory,
                                                shell=True, text=True
                                                ).splitlines()

                for file_name in files:
                    if file_name[:5] == "Notes":
                        day_specified = len(file_name) > 13
                        if day_specified:
                            day = file_name[14:16]

                            file_in_window = not (
                                (year == start_y and month == start_m and day < start_d) or
                                (year == end_y and month == end_m and day > end_d)
                            )
                            if file_in_window:
                                files_to_cat.append(directory + file_name)
                        else:
                            files_to_cat.append(directory + file_name)

    if len(files_to_cat) == 0:
        print("No notes found for the given date range.")
        return

    process = subprocess.Popen(
        ["pdftk", *files_to_cat, "cat", "output",
         docs_path + f"Notes-{start_y}-{start_m}-{start_d}_{end_y}-{end_m}-{end_d}.pdf"])
    process.wait()

    process = subprocess.Popen(
        ["okular", docs_path
         + f"Notes-{start_y}-{start_m}-{start_d}_{end_y}-{end_m}-{end_d}.pdf"])
    process.wait()
    subprocess.run(["rm", docs_path
                    + f"Notes-{start_y}-{start_m}-{start_d}_{end_y}-{end_m}-{end_d}.pdf"])


if len(sys.argv) == 1:
    print(
        fg.customred +
        'command missing - type ' +
        ef.italic +
        'parser help' +
        rs.italic +
        ' for information' +
        fg.rs)

elif sys.argv[1] == 'find':
    try:
        find(sys.argv[2])
    except BaseException:
        print(
            fg.customred +
            'argument missing for ' +
            ef.italic +
            'find' +
            rs.italic +
            fg.rs)

elif sys.argv[1] == 'show':
    if len(sys.argv) == 2:
        show()
    elif len(sys.argv) == 3:
        show(start=sys.argv[2], end=sys.argv[2])
    elif len(sys.argv) == 4:
        show(start=sys.argv[2], end=sys.argv[3])
    else:
        print(fg.customred + 'too many arguments' + fg.rs)

elif sys.argv[1] == 'add':
    if len(sys.argv) > 3:
        add(sys.argv[2], sys.argv[3:])
    else:
        print(fg.customred + 'no keywords to add to key', sys.argv[2] + fg.rs)

elif sys.argv[1] == 'addto':
    try:
        if len(sys.argv) > 3:
            addto(sys.argv[2], sys.argv[3:])
        else:
            print(
                fg.customred +
                'no additional keywords to add to key',
                sys.argv[2] +
                fg.rs)
    except BaseException:
        print(
            fg.customred +
            'no entry for date ',
            sys.argv[2] +
            ' yet' +
            fg.rs)

elif sys.argv[1] == 'remove':
    remove(sys.argv[2])

elif sys.argv[1] == 'backup':
    os.system('cp ' + d + 'dic ' + d + 'dic_bak_' +
              str(datetime.datetime.now())[:10])

elif sys.argv[1] == 'first':
    first()

elif sys.argv[1] == 'last':
    last()

elif sys.argv[1] == 'read':
    if len(sys.argv) < 3:
        print(fg.customred + 'no date or date range given' + fg.rs)
    elif len(sys.argv) == 3:
        read(start=sys.argv[2], end=sys.argv[2])
    elif len(sys.argv) == 4:
        read(start=sys.argv[2], end=sys.argv[3])

elif sys.argv[1] == 'help':
    print(fg.customblue + 'Following commands are available:' + fg.rs + '\n'
          + fg.customred + 'find: keyword' + fg.rs +
          '\n    keyword with spaces must be within quotes. Parse through the keywords for all dates and find matches. \n'
          + fg.customred + 'show: start end' + fg.rs +
          '\n    show all dates with keywords between start and end date. When start and end are not specified, all dates are shown.\n'
          + fg.customred + 'add: date keywords ' + fg.rs +
          '\n    add date of form dd_mm_yyyy, keywords with spaces must be within quotes. \n'
          + fg.customred + 'addto: date keywords ' + fg.rs +
          '\n    add additional keywords to date of form dd_mm_yyyy, keywords with spaces must be within quotes. \n'
          + fg.customred + 'remove: date ' + fg.rs +
          '\n    remove keywords for date (of form dd_mm_yyyy) \n'
          + fg.customred + 'read: start end' + fg.rs +
          '\n    open a PDF file with all handwritten notes between start and end dates. When only start is specified, only that day is shown.\n'
          + fg.customred + 'first:' + fg.rs + '\n    show first date in dictionnary \n'
          + fg.customred + 'last: ' + fg.rs + '\n    show last date in dictionnary \n'
          + fg.customred + 'backup:' + fg.rs + '\n    create backup'
          )

else:
    print(
        fg.customred +
        'unknown command - type ' +
        ef.italic +
        'parser help' +
        rs.italic +
        ' for information' +
        fg.rs)
