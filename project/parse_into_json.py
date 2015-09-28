#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
import const
import xml.etree.cElementTree as ET
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def change_diacritics(instring):
    if type(instring) != unicode and type(instring) != str:
        return instring
    out = instring.replace(u"\u0144", "n")
    out = out.replace(u"\u0105", "a")
    out = out.replace(u"\u0119", "e")
    out = out.replace(u"\u015a", "S")
    out = out.replace(u"\u015b", "s")
    out = out.replace(u"\u0142", "l")
    out = out.replace(u"\u0141", "L")
    out = out.replace(u"\xf3", "o")
    out = out.replace(u"\u017a", "z")
    out = out.replace(u"\u017b", "Z")
    out = out.replace(u"\u017c", "z")
    out = out.replace(u"\u0179", "Z")
    out = out.replace(u"\u00f6", "oe")
    return out


def shape_element(element):
    node = {"created": {}, "type": element.tag}
    # pprint.pprint([i.attrib for i in list(element)])
    if element.tag == "node" or element.tag == "way":
        for key in element.attrib:
            if key in CREATED:
                node["created"][key] = change_diacritics(element.attrib.get(key))
            elif key == "lat" or key == "lon":
                node["pos"] = [float(element.attrib.get("lat")), float(element.attrib.get("lon"))]
            else:
                node[key] = change_diacritics(element.attrib.get(key))
        for e in list(element):
            k = e.get("k")
            v = change_diacritics(e.get("v"))
            if e.tag == "nd":
                if "node_refs" not in node:
                    node["node_refs"] = []
                node["node_refs"].append(e.get("ref"))
            elif "addr" in k:
                if k.count(":") > 1:
                    continue
                if "address" not in node:
                    node["address"] = {}
                subaddr = k.split(":")[1]
                node["address"][subaddr] = v
            # elif lower.search(k) or lower_colon.search(k) or problemchars.search(k):
            #     continue
            else:
                node[k] = v

        return node
    else:
        return None


def process_map(file_in, pretty=False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w", encoding="ascii") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def configure_logger(logger=logging.getLogger('dw')):
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(const.CONSOLE_LOGLEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    logger = logging.getLogger(const.LOGGER_NAME)
    configure_logger(logger)
    logger.info('Script has started')

    process_map(const.MAP_FILENAME)

    logger.info('Script has finished running. Script ran: %s', datetime.datetime.now() - start_time)
    logger.info('-' * 80)
