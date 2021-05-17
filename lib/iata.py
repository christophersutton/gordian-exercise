#############################
#   IATA helper functions   #
#############################
import lib.helpers


def get_price(seat_node, ns, root):
    offerId = seat_node.find("./OfferItemRefs", ns).text
    offerNode = root.find(f'.//*[@OfferItemID="{offerId}"]', ns)
    priceNode = offerNode.find(".//SimpleCurrencyPrice", ns)
    price_in_centavos = int(float(priceNode.text) * 100)
    currency_code = priceNode.get("Code")
    display_price = lib.helpers.getDisplayPrice(price_in_centavos, currency_code)
    return {
        "price_in_centavos": price_in_centavos,
        "currency_code": currency_code,
        "display_price": display_price,
    }


def get_seat_attrs(seat_node, ns, root):
    attrs = set()
    for child in seat_node.iterfind("./SeatDefinitionRef", ns):
        seatDefNode = root.find(f'.//*[@SeatDefinitionID="{child.text}"]', ns)
        attrs.add(seatDefNode.find("./Description/Text", ns).text)
    return attrs


def construct_layout(cabin_node, ns):
    layout = {}
    layoutColumns = []

    for column in cabin_node.iterfind("./CabinLayout/Columns", ns):
        layoutColumns.append(column.get("Position"))
        if column.text == "AISLE" and layoutColumns[-2] != " ":
            layoutColumns.append(" ")

    layout["layout"] = "".join(layoutColumns)

    layout["section_first_row"] = int(
        cabin_node.find("./CabinLayout/Rows/First", ns).text
    )

    layout["section_last_row"] = int(
        cabin_node.find("./CabinLayout/Rows/Last", ns).text
    )
    return layout


def construct_seat(row_num, seat_node, attrs, ns, root):
    seat = {}
    col = seat_node.find("./Column", ns).text
    seat["id"] = f"{row_num}{col}"
    seat["position"] = lib.helpers.get_seat_position(attrs)

    if "AVAILABLE" in attrs and "RESTRICTED" not in attrs:
        price = get_price(seat_node, ns, root)
        seat.update({"available": True, "price": price})
    else:
        seat["available"] = False

    seat["seat_attributes"] = lib.helpers.map_attrs(attrs)
    return seat
