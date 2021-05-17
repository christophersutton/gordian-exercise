############################
# General helper functions #
############################


def getDisplayPrice(centavos, currency):
    symbols = {"USD": "$", "GBP": "£"}
    if currency in symbols.keys():
        return f"{symbols.get(currency)}{centavos/100:.2f}"
    else:
        return "Display price not available"


def map_attrs(attrs):
    res = []
    if any(i in attrs for i in ("EXIT", "ExitRowInd")):
        res.append("exit_row")
    if any(i in attrs for i in ("WING", "Overwing")):
        res.append("overwing")
    if any(i in attrs for i in ("RESTRICTED_RECLINE_SEAT", "Limited Recline")):
        res.append("limited_recline")
    if any(i in attrs for i in ("PREFERENTIAL_SEAT", "Preferred")):
        res.append("preferred")
    if "BulkheadInd" in attrs:
        res.append("bulkhead")
    return res


def filter_row_attrs(attrs):
    return list(filter(lambda attr: attr in ("exit_row", "overwing"), map_attrs(attrs)))


def get_seat_position(attrs):
    if any(i in attrs for i in ("WINDOW", "Window")):
        return "window"
    elif any(i in attrs for i in ("AISLE_SEAT", "Aisle")):
        return "aisle"
    else:
        return "middle"
