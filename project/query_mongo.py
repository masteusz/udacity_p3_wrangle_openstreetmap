#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
import const
import pymongo


def configure_logger(logger=logging.getLogger('dw')):
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(const.CONSOLE_LOGLEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def query_for_overview():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.maps
    poznan = db.poznan

    logger.debug("Number of documents: %r", poznan.find().count())
    logger.debug("Number of nodes: %r", poznan.find({"type": "node"}).count())
    logger.debug("Number of ways: %r", poznan.find({"type": "way"}).count())
    logger.debug("Number of distinct users: %r", len(poznan.distinct("created.user")))

    top3 = poznan.aggregate([
        {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 3}
    ])
    logger.debug("Top 3 contributing users: %r", [i for i in top3])

    avg = poznan.aggregate([
        {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
        {"$group": {"_id": "$created.user", "average": {"$avg": "$count"}}}
    ])
    logger.debug("Average contributions per user: %r", [i for i in avg])


def query_topten():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.maps
    poznan = db.poznan

    doccount = poznan.find().count()

    topten = list(poznan.aggregate([
        {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]))

    topcnt = topten[0].get("count")
    logger.debug("Top user contributions: %r, %r", topcnt, float(topcnt) / doccount * 100)

    top2cnt = topten[0].get("count") + topten[1].get("count")
    logger.debug("Top two users contributions: %r, %r", top2cnt, float(top2cnt) / doccount * 100)

    toptencnt = 0
    for u in topten:
        toptencnt += u.get("count")

    logger.debug("Top ten users contributions: %r, %r", toptencnt, float(toptencnt) / doccount * 100)


def query_fuel():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.maps
    poznan = db.poznan

    res = poznan.aggregate([{"$match": {"amenity": "fuel"}},
                            {"$group": {"_id": "$operator", "count": {"$sum": 1}}},
                            {"$sort": {"count": -1}}, {"$limit": 3}])

    logger.debug(list(res))


def query_credit():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.maps
    poznan = db.poznan



    # res = poznan.aggregate([{"$match": {"wheelchair": "yes"}},
    #                         {"$group": {"_id": "$name", "count": {"$sum": 1}}},
    #                         {"$sort": {"count": -1}}, {"$limit": 10}])

    all_amenities = poznan.find({"amenity": {"$exists": "true"}}).count()
    wheelchair_accessible = poznan.find({"amenity": {"$exists": "true"}, "wheelchair": "yes"}).count()
    logger.debug(all_amenities)
    logger.debug(wheelchair_accessible)


if __name__ == "__main__":
    start_time = datetime.datetime.now()
    logger = logging.getLogger(const.LOGGER_NAME)
    configure_logger(logger)
    logger.info('Script has started')

    # query_for_overview()
    # query_topten()
    # query_fuel()
    query_credit()

    logger.info('Script has finished running. Script ran: %s', datetime.datetime.now() - start_time)
    logger.info('-' * 80)
