import os
import locale

CURRENT_LOCALE = locale.getdefaultlocale()[0]


def lookup_location():
    if os.getenv("LAT") and os.getenv("LONG"):
        return float(os.getenv("LAT")), float(os.getenv("LONG"))
    elif os.path.exists("~/location.txt"):
        f = open("~/location.txt")
        lat = float(f.readline().strip())
        long = float(f.readline().strip())
        return lat, long
    elif os.path.exists(os.path.join(os.path.split(__file__)[0], "location.txt")):
        f = open("location.txt")
        lat = float(f.readline().strip())
        long = float(f.readline().strip())
        return lat, long
    else:
        return 0, 0


def load_locale():
    locales = {}
    for file in os.listdir():
        if file.startswith("locale_"):
            name = file.split(".")[0].replace("locale_", "")
            locales[name] = {}
            with open(file, "r", encoding="utf-8") as fobj:
                for line in fobj:
                    line = line.strip().split("=")
                    locales[name][line[0]] = line[1]
    return locales


def locale(string, locales):
    if CURRENT_LOCALE in locales:
        if string in locales[CURRENT_LOCALE]:
            return locales[CURRENT_LOCALE][string]
        else:
            return string
    elif CURRENT_LOCALE.split("_")[0] in locales:
        if string in locales[CURRENT_LOCALE.split("_")[0]]:
            return locales[CURRENT_LOCALE.split("_")[0]][string]
        else:
            return string
    else:
        return string
