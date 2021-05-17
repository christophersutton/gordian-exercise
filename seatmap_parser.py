import os, sys, argparse, json
import xml.etree.ElementTree as ET
# import project functions
import lib.helpers, lib.opentravel, lib.iata


def main():

    def construct_layout(cabin_node):
        if source == OPENTRAVEL:
            return lib.opentravel.construct_layout(cabin_node, ns)
        else:
            return lib.iata.construct_layout(cabin_node, ns)

    def construct_rows(cabin_node):
        rows = []
        for row in cabin_node.iterfind(f"./{row_xpath}", ns):
            seats = []
            seats_attrs = set()

            row_num = (
                int(row.get("RowNumber"))
                if source == OPENTRAVEL
                else int(row.find("./Number", ns).text)
            )

            # Need to see other examples from IATA to determine how they're 
            # defnining cabin class, for now defaulting to economy for IATA
            cabin_class = row.get("CabinType") if source == OPENTRAVEL else "Economy"

            for seat_node in row.iterfind(f"./{seat_xpath}", ns):
                if source == OPENTRAVEL:
                    attrs = lib.opentravel.get_seat_attrs(seat_node, ns)
                    seat = lib.opentravel.construct_seat(seat_node, attrs, ns)
                    seats_attrs.update(attrs)
                    seats.append(seat)
                else:
                    attrs = lib.iata.get_seat_attrs(seat_node, ns, root)
                    seat = lib.iata.construct_seat(row_num, seat_node, attrs, ns, root)
                    seats_attrs.update(attrs)
                    seats.append(seat)

            row_attrs = lib.helpers.filter_row_attrs(seats_attrs)

            rows.append(
                {
                    "row_number": row_num,
                    "cabin_class": cabin_class,
                    "row_attributes": row_attrs,
                    "seats": seats,
                }
            )

        rows.sort(key=lambda row: row["row_number"])
        return rows

    # load file
    print("#### Loading file")
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    file = parser.parse_args().file

    # exit if not provided an xml file
    basename = os.path.basename(file)
    [filename, extension] = os.path.splitext(basename)
    if extension != ".xml":
        sys.exit("Exiting: requires XML file")

    # set up namespace dictionary and check for validity of file schema
    print("#### Validating schema")
    OPENTRAVEL = "http://www.opentravel.org/OTA/2003/05/common/"
    IATA = "http://www.iata.org/IATA/EDIST/2017.2"

    ns = dict([node for _, node in ET.iterparse(file, events=["start-ns"])])

    if not any(s in ns.values() for s in (OPENTRAVEL, IATA)):
        sys.exit("Invalid schema, please provide IATA or OpenTravel schema")

    # Set up branching variable and xpath routes. Would likely use dictionaries
    # to handle additional schema types, but keeping it simple for now to meet
    # base requirements of this assignments
    source = OPENTRAVEL if OPENTRAVEL in ns.values() else IATA
    seatmap_xpath = "ns:SeatMapDetails" if source == OPENTRAVEL else "SeatMap"
    cabin_xpath = "ns:CabinClass" if source == OPENTRAVEL else "Cabin"
    row_xpath = "ns:RowInfo" if source == OPENTRAVEL else "Row"
    seat_xpath = "ns:SeatInfo" if source == OPENTRAVEL else "Seat"

    # Start parsing
    print("#### Parsing File")
    tree = ET.parse(file)
    root = tree.getroot()
    
    # create our seatmap
    sections = []
    for seatmap in root.iterfind(f".//{seatmap_xpath}", ns):
        for section in seatmap.iterfind(f"./{cabin_xpath}", ns):
            details = {}
            details["section_summary"] = construct_layout(section)
            details["rows"] = construct_rows(section)
            sections.append(details)

    # Write to disk
    print("#### Writing file")
    f = open(f"./output/{filename}_parsed.json", "w")
    f.write(json.dumps(sections, ensure_ascii=False))
    f.close()

    print("#### File converted")


if __name__ == "__main__":
    main()


### todo:
### line 58 seatmap1, lavatory, line 76 bulkhead
