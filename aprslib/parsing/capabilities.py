import re
from aprslib.exceptions import UnknownFormat
from aprslib.exceptions import ParseError

__all__ = [
        'parse_capabilities',
        ]

def parse_capabilities(body):
    capability_data = {}
    print(body)
    # Parse station capabilities message
    try:
        kvpairs = body.split(",")
        type = kvpairs[0]
        del(kvpairs[0])

        for pair in kvpairs:
            if '=' in pair:
                key, value = pair.split("=")
                capability_data[key] = value

        capabilities = {
            'type': type,
            'data': capability_data
        }

        parsed = {
            'format': 'station-capability',
            'capabilities': capabilities
        }

    except (UnknownFormat,ParseError) as ukf:
        raise

    return('', parsed)
