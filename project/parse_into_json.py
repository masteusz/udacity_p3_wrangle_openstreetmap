import logging
import datetime
import const
import xml.etree.cElementTree as ET
import re


def count_tags(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    tagdict = {root.tag: 1}
    fringe = list(root)
    cnt = 0
    while len(fringe) > 0:
        cnt += 1
        current = fringe[0]
        fringe = fringe[1:]
        fringe.extend(list(current))
        if current.tag not in tagdict:
            tagdict[current.tag] = 0
        tagdict[current.tag] += 1
        if cnt % 100 == 0:
            logger.debug(tagdict)
    return tagdict


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        k = element.attrib.get("k")
        if lower.search(k):
            keys["lower"] += 1
        elif lower_colon.search(k):
            keys["lower_colon"] += 1
        elif problemchars.search(k):
            logger.debug(k)
            keys["problemchars"] += 1
        else:
            logger.debug(k)
            keys["other"] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


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

    logger.debug(process_map(const.MAP_FILENAME))

    logger.info('Script has finished running. Script ran: %s', datetime.datetime.now() - start_time)
    logger.info('-' * 80)
