#############################
# OpenTravel helper methods #
#############################
import lib.helpers


def get_price(seat_node, ns):
    priceNode = seat_node.find(".//ns:Fee", ns)
    # Assuming for this exercise based on file that all prices given in centavos
    price_in_centavos = int(priceNode.get("Amount"))
    currency_code = priceNode.get("CurrencyCode")
    display_price = lib.helpers.getDisplayPrice(price_in_centavos, currency_code)
    return {
        "price_in_centavos": price_in_centavos,
        "currency_code": currency_code,
        "display_price": display_price,
    }


def get_seat_attrs(seat_node, ns):
    attrs = set()
    for child in seat_node.iterfind("./ns:Features", ns):
        attr = child.get("extension") if child.text == "Other_" else child.text
        attrs.add(attr)
    for key, value in seat_node.find("./ns:Summary", ns).attrib.items():
        if value == "true":
            attrs.add(key)
    for key, value in seat_node.attrib.items():
        if value == "true":
            attrs.add(key)
    return attrs


def construct_layout(cabin_node, ns):
    layout = {}
    rows = []
    layout["layout"] = cabin_node.get("Layout")
    for el in cabin_node.iterfind("./*[@RowNumber]", ns):
        rows.append(int(el.get("RowNumber")))
    layout["section_first_row"] = min(rows)
    layout["section_last_row"] = max(rows)
    return layout


def construct_seat(seat_node, attrs, ns):
    seat = {}
    seat["id"] = seat_node.find("./ns:Summary", ns).get("SeatNumber")
    seat["position"] = lib.helpers.get_seat_position(attrs)
    if "AvailableInd" in attrs:
        price = get_price(seat_node, ns)
        seat.update({"available": True, "price": price, "type": "seat"})
    else:
        seat_type = "lavatory" if "Lavatory" in attrs else "seat"
        seat.update({"available": False, "type": seat_type})

    seat["seat_attributes"] = lib.helpers.map_attrs(attrs)
    return seat
