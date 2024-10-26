from aprslib.exceptions import UnknownFormat
from aprslib.exceptions import ParseError
from aprslib.parsing.position import *

# Parsing an item report is almost identical to a postition report except the item name
# is variable length (3-9 chars) and not padded to 9 chars.
def parse_item(packet_type, body):
    body, result = parse_position(packet_type, body)

    if (result['format'] is not None):
        # Since an item report conveys the same data as a position report,
        # append '-item-report' to indicate the difference.
        result.update({
            'format': '%s%s' % (result['format'], '-item-report'),
        })

    return (body, result)
