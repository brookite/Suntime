from math import *
import datetime
from suntimelib import *


latitude, longitude = read_coords(__file__)
# longitude is positive for East and negative for West


def plot(*args):
    import pylab
    import matplotlib.dates
    for array in args:
        xdata = array[1]
        ydata = array[0]
        xdata_float = matplotlib.dates.date2num(xdata)
        axes = pylab.subplot(1, 1, 1)
        axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%y"))
        pylab.plot_date(xdata_float, ydata, fmt="b-")
        pylab.grid()
    pylab.show()


def gui():
    MINRAISETIME = "Minimal raising time: "
    MAXRAISETIME = "Maximal raising time: "
    RAISETIME = "Raising time: "
    MINSETTIME = "Minimal setting time: "
    MAXSETTIME = "Maximal setting time: "
    SETTIME = "Setting time: "
    A, C, N, O = "Astronomical", "Civil", "Nautical", "Official"

    import tkinter
    global latitude, longitude
    root = tkinter.Tk()
    dt = datetime.datetime.now()
    year_label = tkinter.Label(root, text="Year:")
    month_label = tkinter.Label(root, text="Month:")
    day_label = tkinter.Label(root, text="Day:")
    y = tkinter.Entry(root)
    y.insert(0, dt.year)
    m = tkinter.Entry(root)
    m.insert(0, dt.month)
    d = tkinter.Entry(root)
    d.insert(0, dt.day)
    latitude_label = tkinter.Label(root, text="Latitude:")
    longitude_label = tkinter.Label(root, text="Longitude:")
    latfield = tkinter.Entry(root, text=latitude)
    latfield.insert(0, latitude)
    longfield = tkinter.Entry(root, text=longitude)
    longfield.insert(0, longitude)
    radiovar = tkinter.IntVar()
    group = tkinter.LabelFrame(root)
    minmax_radiobutton = tkinter.Radiobutton(root, text='Minimal and Maximum time', variable=radiovar, value=1)
    full_radiobutton = tkinter.Radiobutton(root, text='Full information', variable=radiovar, value=2)
    ovar, avar, cvar, nvar = tkinter.IntVar(), tkinter.IntVar(), tkinter.IntVar(), tkinter.IntVar()
    ovar.set(1)
    avar.set(1)
    cvar.set(1)
    nvar.set(1)
    official_checkbox = tkinter.Checkbutton(group, text=O, variable=ovar, onvalue=1, offvalue=0)
    astronomical_checkbox = tkinter.Checkbutton(group, text=A, variable=avar, onvalue=1, offvalue=0)
    civil_checkbox = tkinter.Checkbutton(group, text=C, variable=cvar, onvalue=1, offvalue=0)
    nautical_checkbox = tkinter.Checkbutton(group, text=N, variable=nvar, onvalue=1, offvalue=0)
    radiovar.set(2)

    def plot_gen():
        global latitude, longitude
        year = int(y.get())
        dt = datetime.datetime.now(datetime.timezone.utc).astimezone()
        utc_offset = dt.utcoffset().seconds // 3600
        latitude = float(latfield.get())
        longitude = float(longfield.get())
        if radiovar.get() == 2:
            plot(calculate_for_year(latitude, longitude, year, "official", True, time_offset=utc_offset),
                 calculate_for_year(latitude, longitude, year, "official", False, time_offset=utc_offset))
        else:
            plot(calculate_minmax_for_year(latitude, longitude, year, True, time_offset=utc_offset),
                 calculate_minmax_for_year(latitude, longitude, year, False, time_offset=utc_offset))

    def push():
        global latitude, longitude
        year = int(y.get())
        month = int(m.get())
        day = int(d.get())
        dt = datetime.datetime.now(datetime.timezone.utc).astimezone()
        utc_offset = dt.utcoffset().seconds // 3600
        latitude = float(latfield.get())
        longitude = float(longfield.get())
        zeniths = []
        if ovar.get() == 1:
            zeniths.append("official")
        if avar.get() == 1:
            zeniths.append("astronomical")
        if cvar.get() == 1:
            zeniths.append("civil")
        if nvar.get() == 1:
            zeniths.append("nautical")
        if radiovar.get() == 2:
            grp = (calculate_groups(latitude, longitude, year, month, day, True, utc_offset, zeniths),
                   calculate_groups(latitude, longitude, year, month, day, False, utc_offset, zeniths))
            buffer = RAISETIME + "\n\n"
            for g in grp[0]:
                if g == "official":
                    buffer += O + ": " + ":".join(decimal_to_time(grp[0][g])) + '\n'
                elif g == "astronomical":
                    buffer += A + ": " + ":".join(decimal_to_time(grp[0][g])) + '\n'
                elif g == "civil":
                    buffer += C + ": " + ":".join(decimal_to_time(grp[0][g])) + '\n'
                elif g == "nautical":
                    buffer += N + ": " + ":".join(decimal_to_time(grp[0][g])) + '\n'
            buffer += "\n\n" + SETTIME + "\n\n"
            for g in grp[1]:
                if g == "official":
                    buffer += O + ": " + ":".join(decimal_to_time(grp[1][g])) + '\n'
                elif g == "astronomical":
                    buffer += A + ": " + ":".join(decimal_to_time(grp[1][g])) + '\n'
                elif g == "civil":
                    buffer += C + ": " + ":".join(decimal_to_time(grp[1][g])) + '\n'
                elif g == "nautical":
                    buffer += N + ": " + ":".join(decimal_to_time(grp[1][g])) + '\n'
        else:
            grp = (calculate_min_max(latitude, longitude, year, month, day, True, utc_offset),
                   calculate_min_max(latitude, longitude, year, month, day, False, utc_offset))
            s_time = decimal_to_time(grp[0]), decimal_to_time(grp[1])
            buffer = ""
            buffer += MINRAISETIME + ":".join(s_time[0][0]) + '\n'
            buffer += MAXRAISETIME + ":".join(s_time[0][1]) + '\n'
            buffer += MINSETTIME + ":".join(s_time[1][0]) + '\n'
            buffer += MAXSETTIME + ":".join(s_time[1][1]) + '\n'
        result_field.delete(0.0, "end")
        result_field.insert(0.0, buffer)

    plot_button = tkinter.Button(root, text="Create plot", command=plot_gen, width=10)
    push_button = tkinter.Button(root, text="Push", width=10, command=push)
    resscroll = tkinter.Scrollbar(root)
    result_field = tkinter.Text(root, width=50, height=15)
    result_field['yscrollcommand'] = resscroll.set
    resscroll.config(command=result_field.yview)
    result_field.grid(row=0, column=0, rowspan=2, columnspan=2)
    resscroll.grid(row=0, column=0, rowspan=2, columnspan=2)
    year_label.grid(row=2, column=0)
    y.grid(row=2, column=1)
    month_label.grid(row=3, column=0)
    m.grid(row=3, column=1)
    day_label.grid(row=4, column=0)
    d.grid(row=4, column=1)
    latitude_label.grid(row=5, column=0)
    latfield.grid(row=5, column=1)
    longitude_label.grid(row=6, column=0)
    longfield.grid(row=6, column=1)
    plot_button.grid(row=7, column=0, padx=5, pady=5)
    push_button.grid(row=7, column=1, padx=5, pady=5)
    official_checkbox.grid(row=0, column=0)
    astronomical_checkbox.grid(row=0, column=1)
    civil_checkbox.grid(row=0, column=2)
    nautical_checkbox.grid(row=0, column=3)
    full_radiobutton.grid(row=8, column=0, columnspan=2)
    group.grid(row=9, column=0, columnspan=4)
    minmax_radiobutton.grid(row=10, column=0, columnspan=2)
    root.title("Suntime")
    root.mainloop()


if __name__ == "__main__":
    gui()
