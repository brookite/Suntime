from math import *
import datetime

zenith = {
    "official": cos(radians(90 + 5 / 6)),
    "civil": cos(radians(96)),
    "nautical": cos(radians(102)),
    "astronomical": cos(radians(108))
}


def _day_of_year(year, month, day):
    N1 = floor(275 * month / 9)
    N2 = floor((month + 9) / 12)
    N3 = (1 + floor((year - 4 * floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30
    return N


def _longitude_to_hour(longitude, N, rise=True):
    lngHour = longitude / 15
    if rise:
        t = N + ((6 - lngHour) / 24)
    else:
        t = N + ((18 - lngHour) / 24)
    return t, lngHour


def _sun_mean_anomaly(t):
    M = (0.9856 * t) - 3.289
    return M


def _sun_true_longitude(M):
    NM = M
    M = radians(M)
    L = NM + (1.916 * sin(M)) + (0.020 * sin(M * 2)) + 282.634
    if L < 0:
        L += 360
    if L > 359:
        L -= 360
    return L


def _sun_right_ascension(L):
    RA = degrees(atan(0.91764 * tan(radians(L))))
    """
    if RA < -0:
        RA += 360
    """
    if RA > 359:
        RA -= 360
    Lquadrant = (floor(L / 90)) * 90
    RAquadrant = (floor(RA / 90)) * 90
    RA = RA + (Lquadrant - RAquadrant)
    RA = RA / 15
    return RA


def _sun_declination(L):
    sinDec = 0.39782 * sin(radians(L))
    cosDec = cos(asin(sinDec))
    return sinDec, cosDec


def _local_hour_angle(latitude, sinDec, cosDec, current_zenith, rise=True):
    cosH = (current_zenith - (sinDec * sin(radians(latitude)))) / (cosDec * cos(radians(latitude)))
    if cosH > 1:
        # print("the sun never rises on this location (on the specified date)")
        return None
    if cosH < -1:
        # print("the sun never sets on this location (on the specified date)")
        return None
    if rise:
        H = 360 - degrees(acos(cosH))
    else:
        H = degrees(acos(cosH))
    H = H / 15
    return H


def _get_time(H, RA, t, lngHour, local_offset):
    if H is None:
        return -1
    T = H + RA - (0.06571 * t) - 6.622
    UT = T - lngHour
    if UT > 23:
        UT -= 24
    if UT < 0:
        UT += 24
    localT = UT + local_offset
    return localT


def calculate(latitude, longitude, year, month, day, current_zenith, rise, time_offset=0):
    current_zenith = zenith[current_zenith]
    N = _day_of_year(year, month, day)
    t, lngHour = _longitude_to_hour(longitude, N, rise)
    M = _sun_mean_anomaly(t)
    L = _sun_true_longitude(M)
    RA = _sun_right_ascension(L)
    sinDec, cosDec = _sun_declination(L)
    H = _local_hour_angle(latitude, sinDec, cosDec, current_zenith, rise)
    time = _get_time(H, RA, t, lngHour, time_offset)
    return time


def decimal_to_time(value):
    if hasattr(value, "__iter__"):
        value = list(value)
        for i in range(len(value)):
            h = int(value[i])
            minutes = (value[i] - h) * 60
            value[i] = [str(h), str(int(minutes))]
            if len(value[i][0]) == 1:
                value[i][0] = "0" + value[i][0]
            if len(value[i][1]) == 1:
                value[i][1] = "0" + value[i][1]
        return value
    else:
        h = str(int(value))
        minutes = str(int((value - int(h)) * 60))
        if len(h) == 1:
            h = "0" + h
        if len(minutes) == 1:
            minutes = "0" + minutes
        return h, minutes


def calculate_all(latitude, longitude, year, month, day, rise, time_offset=0):
    a = []
    for z in zenith:
        c = calculate(latitude, longitude, year, month, day, z, rise, time_offset)
        a.append(c)
    a.sort()
    for i in a:
        if i == -1 or i > 24:
            a.remove(i)
    return a


def calculate_groups(latitude, longitude, year, month, day, rise, time_offset=0, zen=zenith.keys()):
    a = {}
    for z in zen:
        c = calculate(latitude, longitude, year, month, day, z, rise, time_offset)
        a[z] = c
    todel = []
    for i in a:
        if a[i] == -1 or a[i] > 24:
            todel.append(i)
    for i in todel:
        a.pop(i)
    return a


def calculate_min_max(latitude, longitude, year, month, day, rise, time_offset=0):
    a = calculate_all(latitude, longitude, year, month, day, rise, time_offset)
    return min(a), max(a)


def calculate_for_year(latitude, longitude, year, current_zenith, rise, time_offset=0):
    array = []
    dates = []
    first = datetime.datetime(year, 1, 1).timestamp()
    end = datetime.datetime(year, 12, 31).timestamp()
    days = int((end - first) // 86400)
    for i in range(days):
        t = first + 86400 * (i + 1)
        dt = datetime.datetime.fromtimestamp(t)
        array.append(calculate(latitude, longitude, year, dt.month, dt.day, current_zenith, rise, time_offset))
        dates.append(dt)
    return array, dates


def calculate_minmax_for_year(latitude, longitude, year, rise, time_offset=0):
    array = []
    dates = []
    first = datetime.datetime(year, 1, 1).timestamp()
    end = datetime.datetime(year, 12, 31).timestamp()
    days = int((end - first) // 86400)
    for i in range(days):
        t = first + 86400 * (i + 1)
        dt = datetime.datetime.fromtimestamp(t)
        if rise:
            array.append(calculate_min_max(latitude, longitude, year, dt.month, dt.day, rise, time_offset)[0])
        else:
            array.append(calculate_min_max(latitude, longitude, year, dt.month, dt.day, rise, time_offset)[1])
        dates.append(dt)
    return array, dates


def day_of_year_to_date(year, day_of_year):
    first = datetime.datetime(year, 1, 1).timestamp()
    seconds = day_of_year * 86400
    dt = datetime.datetime.fromtimestamp(first + seconds)
    return dt.year, dt.month, dt.day
