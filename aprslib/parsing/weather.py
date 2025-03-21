import re
from aprslib.exceptions import ParseError

__all__ = [
    'parse_weather',
    'parse_weather_data',
    'parse_raw_weather'
    ]

# constants
# wind is in miles per hour
wind_multiplier = 0.44704
# Spec 1.1 Rain is in hundredths of an inch.
rain_multiplier = 0.254

key_map = {
    'g': 'wind_gust',
    'c': 'wind_direction',
    't': 'temperature',
    'S': 'wind_speed',
    'r': 'rain_1h',
    'p': 'rain_24h',
    'P': 'rain_since_midnight',
    'h': 'humidity',
    'b': 'pressure',
    'l': 'luminosity',
    'L': 'luminosity',
    's': 'snow',
    '#': 'rain_raw',
}
val_map = {
    'g': lambda x: int(x) * wind_multiplier,
    'c': lambda x: int(x),
    'S': lambda x: int(x) * wind_multiplier,
    't': lambda x: (float(x) - 32) / 1.8,
    'r': lambda x: int(x) * rain_multiplier,
    'p': lambda x: int(x) * rain_multiplier,
    'P': lambda x: int(x) * rain_multiplier,
    'h': lambda x: 100 if int(x) == 0 else int(x),
    'b': lambda x: float(x) / 10,
    'l': lambda x: int(x) + 1000,
    'L': lambda x: int(x),
    's': lambda x: float(x) * 25.4,
    '#': lambda x: int(x),
}

def parse_weather_data(body):
    parsed = {}

    # parse weather data
    # SW 9-30-24 - Add \. as course and speed can contain ...
    body = re.sub(r"^([0-9\.]{3})/([0-9\.]{3})", "c\\1s\\2", body)
    body = body.replace('s', 'S', 1)

    # SW 10-01-24 - Make matchall regex compatible with findall regex
    # match as many parameters from the start, rest is comment
    data = re.match(r"^([cSgtrpPlLs#][0-9\-\. ]{3}|t[0-9\. \-]{2}|h[0-9\. ]{2}|b[0-9\. ]{5}|s[0-9\. ]{2}|s[0-9\. ]{1})+", body)
    if data:
        data = data.group()
        # split out data from comment
        body = body[len(data):]
        # parse all weather parameters
        data = re.findall(r"([cSgtrpPlLs#]\d{3}|t-\d{2}|h\d{2}|b\d{5}|s\.\d{2}|s\d\.\d)", data)
        data = map(lambda x: (key_map[x[0]] , val_map[x[0]](x[1:])), data)
        parsed.update(dict(data))

    return (body, parsed)

def parse_weather(body):
    match = re.match(r"^(\d{8})c[\. \d]{3}s[\. \d]{3}g[\. \d]{3}t[\. \d]{3}", body)
    if not match:
        raise ParseError("Invalid positionless weather report format")

    comment, weather = parse_weather_data(body[8:])

    parsed = {
        'format': 'wx',
        'wx_raw_timestamp': match.group(1),
        'comment': comment.strip(' '),
        'weather': weather,
        }

    return ('', parsed)

# Parse peet Ultimeter raw packet data
# https://www.peetbros.com/HTML_Pages/faqs.htm#Q5
def parse_raw_weather(body):

    if (body[0:4] == 'ULTW'):
        match = re.match(r"^ULTW([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)?([0-9a-fA-F]{4}|----)?", body)

        if not match:
            raise ParseError("Invalid raw weather report format")

        wxparsed = {
            'wind_gust': ((int(match.group(1), 16) / 3.6) / 10) if match.group(1) != "----" else None,
            'wind_direction': (round(int(match.group(2), 16) * 1.41176)) if match.group(2) != "----" else None,
            'temperature': (((int(match.group(3), 16) / 10) - 32)/ 1.8) if match.group(3) != "----" else None,
            'rain_since_midnight': ((int(match.group(4), 16) * 0.254)) if match.group(4) != "----" else None,
            'pressure': (int(match.group(5), 16) / 10) if match.group(5) != "----" else None,
            'humidity': (int(match.group(9), 16) / 10) if match.group(9) != "----" else None,
            'rain_since_midnight': ((int(match.group(12), 16) * 0.254)) if match.group(12) != "----" else None,
            'wind_speed': ((int(match.group(13), 16) / 3.6) / 10) if match.group(13) is not None and match.group(13) != "----" else None,  # Group 13 is not available on some models
            }

        weather = {}
        for key, value in wxparsed.items():
            if (value is not None):
                weather[key] = value

        parsed = {
            'format': 'wxraw',
            'weather': weather,
            }
        return ('', parsed)

    elif (body[0:1] == '!'):
        match = re.match(r"^!([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)([0-9a-fA-F]{4}|----)?([0-9a-fA-F]{4}|----)?", body)

        if not match:
            raise ParseError("Invalid raw weather report format")

        wxparsed = {
            'wind_gust': ((int(match.group(1), 16) / 3.6) / 10) if match.group(1) != "----" else None,
            'wind_direction': (round(int(match.group(2), 16) * 1.41176)) if match.group(2) != "----" else None,
            'temperature': (((int(match.group(3), 16) / 10) - 32)/ 1.8) if match.group(3) != "----" else None,
            'rain_since_midnight': ((int(match.group(4), 16) * 0.254)) if match.group(4) != "----" else None,
            'pressure': (int(match.group(5), 16) / 10) if match.group(5) != "----" else None,
            'humidity': (int(match.group(7), 16) / 10) if match.group(7) != "----" else None,
            'rain_since_midnight': ((int(match.group(11), 16) * 0.254)) if match.group(11) != "----" else None,
            'wind_speed': ((int(match.group(12), 16) / 3.6) / 10) if match.group(12) != "----" else None,
            }

        weather = {}
        for key, value in wxparsed.items():
            if (value is not None):
                weather[key] = value

        parsed = {
            'format': 'wxraw',
            'weather': weather,
            }
        return ('', parsed)

    else:
        return ('', {})
