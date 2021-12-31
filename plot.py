from matplotlib import pyplot as plt
from matplotlib import dates
import datetime
import corelib


def time_handler(arg):
    if isinstance(arg, datetime.datetime):
        return arg.hour + arg.minute / 60 + arg.second / 3600
    elif isinstance(arg, datetime.timedelta):
        return arg.total_seconds() / 3600
    else:
        return arg


def plotdata_template(year, location, depression, *args):
    depression = corelib.cmp_depression(depression)
    x = []
    y_plots = [[] for i in range(len(args))]
    end = datetime.datetime(year, 12, 31).timestamp()
    start = datetime.datetime(year, 1, 1).timestamp()
    for i in range(int(end - start) // 86400):
        date = datetime.datetime.fromtimestamp(start + 86400 * (i + 1))
        x.append(date)
        data = corelib.get_data(location, depression, date)
        for i in range(len(args)):
            y_plots[i].append(time_handler(data[args[i]]))
    return x, *y_plots


def dawn_dusk(year, location, depression):
    return plotdata_template(year, location, depression, "dawn", "dusk")


def sunrise_sunset(year, location, depression):
    return plotdata_template(year, location, depression, "sunrise", "sunset")


def noon_midnight(year, location, depression):
    return plotdata_template(year, location, depression, "noon", "midnight")


def day_night_length(year, location, depression):
    return plotdata_template(year, location, depression, "daylength", "nightlength")


def build_plot(x, *y, title=None, xlabel=None, ylabel=None):
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1)
    axes.xaxis.set_major_formatter(dates.DateFormatter("%d.%m.%y"))
    plt.xticks(rotation='vertical')
    pairs = []
    for j in y:
        pairs.append(x)
        pairs.append(j)
    plt.plot(*pairs)
    plt.grid()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()


def build(location, datetime, depression, index, tz=None):
    if index == 0:
        build_plot(*dawn_dusk(datetime.year, location, depression))
    elif index == 1:
        build_plot(*sunrise_sunset(datetime.year, location, depression))
    elif index == 2:
        build_plot(*noon_midnight(datetime.year, location, depression))
    elif index == 3:
        build_plot(*day_night_length(datetime.year, location, depression))
