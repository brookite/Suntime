from astral import LocationInfo
from astral.sun import sun, midnight, daylight, \
    night, golden_hour, blue_hour, twilight, elevation, zenith, azimuth
from astral import moon
from utils import locale
import datetime
import calendar


def get_location(lat, long, name="Unnamed region"):
    loc = LocationInfo()
    loc.name = name
    loc.latitude = lat
    loc.longitude = long
    return loc


def compile_date(year, month, day):
    return datetime.date(year, month, day)


def get_data(location, date: datetime.datetime, tz=None):
    data = sun(location.observer, date=date, tzinfo=tz)
    prev_data = sun(location.observer, date=date - datetime.timedelta(days=1), tzinfo=tz)
    next_data = sun(location.observer, date=date + datetime.timedelta(days=1), tzinfo=tz)
    data['moon_phase'] = moon.phase(date)
    data["midnight"] = midnight(location.observer, date=date)
    data["daylight"] = daylight(location.observer, date=date)
    data["twilight"] = twilight(location.observer, date=date)
    data["night"] = night(location.observer, date=date)
    data["golden_hour"] = golden_hour(location.observer, date=date)
    data["blue_hour"] = blue_hour(location.observer, date=date)
    data["solar_elevation"] = elevation(location.observer, dateandtime=date)
    data["zenith"] = zenith(location.observer, dateandtime=date)
    data["azimuth"] = azimuth(location.observer, dateandtime=date)
    data["daylength"] = data["dusk"] - data["dawn"]
    data["nightlength"] = next_data["dawn"] - data["dusk"]
    data["daylength_change"] = data["daylength"].total_seconds() - \
        (prev_data["dusk"] - prev_data["dawn"]).total_seconds()
    data["nightlength_change"] = data["nightlength"].total_seconds() - \
        (data["dawn"] - prev_data["dusk"]).total_seconds()
    return data


def _find_minmax(param1, param2, min_condition=False, ignore_value=None, function=None):
    if param1 is ignore_value:
        return param2
    elif param2 is ignore_value:
        return param1
    if function:
        cmp1, cmp2 = function(param1), function(param2)
    else:
        cmp1, cmp2 = param1, param2
    if min_condition:
        res = min(cmp1, cmp2)
    else:
        res = max(cmp1, cmp2)
    return param1 if res == cmp1 else param2


def get_calculated_data(location, date, tz=None):
    calcdata = {}
    calcdata["min_daylength"] = [None, None]
    calcdata["max_daylength"] = [None, None]
    calcdata["min_nightlength"] = [None, None]
    calcdata["max_nightlength"] = [None, None]

    def time_compare(d):
        return d.time()

    for n in range(int((datetime.date(date.year, 12, 31) - datetime.date(date.year, 1, 1)).days)):
        iterdate = datetime.date(date.year, 1, 1) + datetime.timedelta(days=n)
        data = get_data(location, datetime.datetime(iterdate.year, iterdate.month, iterdate.day), tz)
        calcdata["early_dawn"] = _find_minmax(calcdata.get("early_dawn"),
                                              data["dawn"], min_condition=True, function=time_compare)
        calcdata["early_sunrise"] = _find_minmax(calcdata.get("early_sunrise"),
                                                 data["sunrise"], min_condition=True, function=time_compare)
        calcdata["early_sunset"] = _find_minmax(calcdata.get("early_sunset"),
                                                data["sunset"], min_condition=True, function=time_compare)
        calcdata["early_dusk"] = _find_minmax(calcdata.get("early_dusk"),
                                              data["dusk"], min_condition=True, function=time_compare)
        calcdata["late_dawn"] = _find_minmax(calcdata.get("late_dawn"),
                                             data["dawn"], min_condition=False, function=time_compare)
        calcdata["late_sunrise"] = _find_minmax(calcdata.get("late_sunrise"),
                                                data["sunrise"], min_condition=False, function=time_compare)
        calcdata["late_sunset"] = _find_minmax(calcdata.get("late_sunset"),
                                               data["sunset"], min_condition=False, function=time_compare)
        calcdata["late_dusk"] = _find_minmax(calcdata.get("late_dusk"),
                                             data["dusk"], min_condition=False, function=time_compare)
        calcdata["late_noon"] = _find_minmax(calcdata.get("late_noon"),
                                             data["noon"], min_condition=False, function=time_compare)
        calcdata["late_midnight"] = _find_minmax(calcdata.get("late_midnight"),
                                                 data["midnight"], min_condition=False, function=time_compare)
        calcdata["early_noon"] = _find_minmax(calcdata.get("early_noon"),
                                              data["noon"], min_condition=True, function=time_compare)
        calcdata["early_midnight"] = _find_minmax(calcdata.get("early_midnight"),
                                                  data["midnight"], min_condition=True, function=time_compare)

        calcdata["min_daylength"][1] = _find_minmax(calcdata.get("min_daylength")[1],
                                                    data["daylength"], min_condition=True)
        calcdata["min_daylength"][0] = iterdate if calcdata["min_daylength"][1] == data["daylength"] else calcdata["min_daylength"][0]
        calcdata["max_daylength"][1] = _find_minmax(calcdata.get("max_daylength")[1],
                                                    data["daylength"], min_condition=False)
        calcdata["max_daylength"][0] = iterdate if calcdata["max_daylength"][1] == data["daylength"] else calcdata["max_daylength"][0]

        calcdata["min_nightlength"][1] = _find_minmax(calcdata.get("min_nightlength")[1],
                                                      data["nightlength"], min_condition=True)
        calcdata["min_nightlength"][0] = iterdate if calcdata["min_nightlength"][1] == data["nightlength"] else calcdata["min_nightlength"][0]
        calcdata["max_nightlength"][1] = _find_minmax(calcdata.get("max_nightlength")[1],
                                                      data["nightlength"], min_condition=False)
        calcdata["max_nightlength"][0] = iterdate if calcdata["max_nightlength"][1] == data["nightlength"] else calcdata["max_nightlength"][0]

    startmonth = datetime.datetime(date.year, date.month, 1)
    startmonthdata = get_data(location, startmonth, tz)
    endmonth = datetime.datetime(date.year, date.month, calendar.monthrange(date.year, date.month)[1])
    endmonthdata = get_data(location, endmonth, tz)
    calcdata["month_daylength_change"] = endmonthdata["daylength"].total_seconds() - \
        startmonthdata["daylength"].total_seconds()
    calcdata["month_nightlength_change"] = endmonthdata["nightlength"].total_seconds() - \
        startmonthdata["nightlength"].total_seconds()
    return calcdata


def _format(data):
    format_datetime = "%d.%m.%y %H:%M:%S"
    format_date = "%d.%m.%y"
    format_time = "%H:%M:%S"
    if isinstance(data, datetime.datetime):
        return data.strftime(format_datetime)
    elif isinstance(data, datetime.date):
        return data.strftime(format_date)
    elif isinstance(data, datetime.time):
        return data.strftime(format_time)
    elif isinstance(data, float):
        return str(round(data, 2))
    elif isinstance(data, tuple) or isinstance(data, list):
        s = ""
        for key in data:
            s += _format(key) + "; "
        return s
    else:
        return str(data)


def get_string(locales, datetime, location, tz=None):
    data = get_data(location, datetime, tz)
    calc_data = get_calculated_data(location, datetime, tz)
    string = _format(datetime)
    template = string
    template += "\n\n"
    for key in data:
        template += locale(key, locales) + ": " + _format(data[key]) + "\n"
    template += "\n\n"
    for key in calc_data:
        template += locale(key, locales) + ": " + _format(calc_data[key]) + "\n"
    return template
