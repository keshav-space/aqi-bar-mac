#!/usr/bin/env LC_ALL=en_US.UTF-8 /usr/local/bin/python3
#
# <xbar.title>Air Quality Index</xbar.title>
# <xbar.version>v1.1</xbar.version>
# <xbar.author>Keshav Priyadarshi</xbar.author>
# <xbar.author.github>keshav.space</xbar.author.github>
# <xbar.desc>Real-time Air Quality Index. You need to set the API_TOKEN and CITY in this plugin.</xbar.desc>
# <xbar.image>https://raw.githubusercontent.com/keshav-space/aqi-bar-mac/main/Screenshot.png</xbar.image>

from datetime import datetime, timedelta
import json
import os
import socket

# ---------------------------------------------------------------------------------------------------------------------
# Put your API Token from https://aqicn.org/api/
API_TOKEN = ""

#Major city or location URL path after https://aqicn.org/city/
CITY = [
    'india/kolkata/jadavpur',
    'delhi/bramprakash-ayurvedic-hospital--najafgarh', 
    'india/bengaluru/hebbal'
]

# Name of city feed to CITY = []
CITY_NAME = [
    'Kolkata',
    'Delhi', 
    'Bengaluru'
]


# ---------------------------------------------------------------------------------------------------------------------

PARAMETERS = {
    'co' : 'CO',
    'dew' : 'DEW PT',
    'h' : 'HUMIDITY',
    'no2' : 'NO₂',
    'o3' : 'O₃',
    'p' : 'PRESSURE',
    'pm10' : 'PM₁₀',
    'pm25' : 'PM₂.₅',
    'so2' :'SO₂', 
    't' : 'TEMP', 
    'w' :'WIND',
    'uvi' : 'UV Index', 
}

UNIT = {
    'co' : 'ppm',
    'dew' : '°C',
    'h' : '%',
    'no2' : 'ppb',
    'o3' : 'ppb',
    'p' : 'mm.Hg',
    'pm10' : 'μg/m³',
    'pm25' : 'μg/m³',
    'so2' :'ppb', 
    't' : '°C', 
    'w' :'km/h',
    'uvi': '[25 mW/m²]',
}

PAT = ['t', 'p', 'h', 'dew', 'w', 'pm25', 'pm10', 'co', 'so2', 'no2', 'o3', 'uvi']

# Indexing is done a/c to 'U.S. Environmental Protection Agency' Guidelines
INDEX_USEPA = {
    'aqi' : [50, 100, 150, 200, 300, 500],
    # co in ppm
    'co' : [4.4, 9.4, 12.4, 15.4, 30.4],
    #no2 in ppb
    'no2' : [53, 100, 360, 649, 1249],
    #o3 in ppb
    'o3' : [54, 70, 85, 105, 200],
    #ppm10 in mg/m3
    'pm10' : [54, 154, 254, 354, 424],
    #ppm2.5 in mg/m3
    'pm25' : [12, 35.4, 55.4, 150.4, 250.4],
    #so2 in ppb
    'so2' :[35, 75, 185, 304, 604],
    #uvi in multiple of [25 mW/m²]
    'uvi' : [2, 5, 7, 10],
}

sub_max ='₍ₘₐₓ₎'
TOMORROW_DATE = str(datetime.today().date() + timedelta(days=1))
TODAY_DATE = str(datetime.today())

# ---------------------------------------------------------------------------------------------------------------------

LEVEL_COLOR = ['\033[38;5;46m','\033[38;5;226m','\033[38;5;208m','\033[38;5;196m','\033[38;5;129m','\033[38;5;88m','\033[38;5;1m']


EMOJIS = ["😀","🙁","😨","😷","🤢","⚠️","☠️"]

RESET = '\033[0m'
FONT = "| size=13 font='Menlo'"
FONT_SUB = "| size=14 font='Menlo'"
# ---------------------------------------------------------------------------------------------------------------------

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False

def format_name(st,le):
    return st + " "*(le - len(st))

def get_color(key, val):
    if not key in INDEX_USEPA:
        return ''
    critical_point = INDEX_USEPA[key]
    for i in range(len(critical_point)):
        if val <= critical_point[i]:
            return LEVEL_COLOR[i]
    return LEVEL_COLOR[ len(critical_point) ]

def get_update_stat(fdate):
    d_date = datetime.strptime(fdate, "%Y-%m-%d %H:%M:%S")
    diff = datetime.now() - d_date
    sec = diff.seconds
    minutes, sec = divmod(sec, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return str(hours) +' hours ago'
    return str(minutes) + ' minutes ago'


def city_info(raw):
    print('-----')
    primary_width = 20
    format_submenu = '{:<0} {:>8}' + FONT_SUB
    realtime_data = raw['data']['iaqi']
    for key in PAT[:11]:
        if key == 'pm25':
            print('-----')
        name = '--' + format_name(PARAMETERS[key], primary_width)
        color = get_color(key,realtime_data[key]['v'])
        print(format_submenu.format(name + color , str('{:.2f} '.format(realtime_data[key]['v'])) 
            + UNIT[key]))

    uvi_today = raw['data']['forecast']['daily']['uvi']
    for day in uvi_today:
        if day['day'] == TODAY_DATE:
            name = '--' + format_name(PARAMETERS['uvi'], primary_width)
            color = get_color('uvi',day['max'])
            print(format_submenu.format(name + color, str('{:.2f} '.format(day['max']))
                + UNIT['uvi']))
            break

    print('-----')
    print('--Forecast: ', TOMORROW_DATE + FONT_SUB)
    print('-----')
    forecast_data = raw['data']['forecast']['daily']
    for key in forecast_data:
        if key in PARAMETERS:
            for days in forecast_data[key]:
                if days['day'] == TOMORROW_DATE:
                    name = '--' + format_name(PARAMETERS[key]+ sub_max, primary_width)
                    color = get_color(key,days['max'])
                    print(format_submenu.format(name + color, str('{:.2f} '.format(days['max']))
                        + UNIT[key]))
                    break

def print_aqi_scale():
    print('AQI Scale' + FONT)
    print('--AQI Scale [US-EPA 2016]')
    print('-----')
    format_submenu = '{:<5} {:<3} {:>15}' + FONT_SUB
    print(format_submenu.format('--' + LEVEL_COLOR[0] + format_name('000 - 050',10), EMOJIS[0], 
        format_name('Good', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[1] + format_name('051 - 100',10), EMOJIS[1], 
        format_name('Moderate', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[2] + format_name('101 - 150',10), EMOJIS[2], 
        format_name('Quite Unhealthy', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[3] + format_name('151 - 200',10), EMOJIS[3], 
        format_name('Unhealthy', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[4] + format_name('201 - 300',10), EMOJIS[4], 
        format_name('Very Unhealthy', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[5] + format_name('301 - 400',10), EMOJIS[5], 
        format_name(' Hazardous', 15)))
    print(format_submenu.format('--' + LEVEL_COLOR[6] + format_name('401+',10), EMOJIS[6], 
        format_name(' Are You Alive?', 15)))


if __name__ == '__main__':
    if not is_connected():
        print("AQI: 🛰",FONT+"color=red")
        exit()
    fetched_data = []

    for city in CITY:
        library = 'curl --silent '
        api = "https://api.waqi.info/feed/"+ city +"/?token="+API_TOKEN
        cmd = library + "'" + api + "'"
        output = os.popen(cmd).read()
        json_output = json.loads(output)
        fetched_data.append(json_output)


    for i in range(len(fetched_data)):
        color = get_color('aqi',fetched_data[i]['data']['aqi'])
        dis_city = format_name("AQI " + CITY_NAME[i] + ": ", 10)
        print(dis_city,  color + str(fetched_data[i]['data']['aqi']) 
            + " " + EMOJIS[LEVEL_COLOR.index(color)] + RESET + FONT)

    print("---")
    for i in range(len(CITY_NAME)):
        print(CITY_NAME[i] + FONT )
        print('--' + CITY_NAME[i] + '| href='+fetched_data[i]['data']['city']['url'] + FONT_SUB)
        color = get_color('aqi',fetched_data[i]['data']['aqi'])
        print(format_name("--AQI :", 10),  color + str(fetched_data[i]['data']['aqi']) 
            + " " + EMOJIS[LEVEL_COLOR.index(color)] + RESET + FONT)
        print('--Last Update:', get_update_stat(fetched_data[i]['data']['time']['s']) + FONT_SUB)
        city_info(fetched_data[i])
    print_aqi_scale()
