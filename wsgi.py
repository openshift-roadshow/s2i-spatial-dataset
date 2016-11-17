from __future__ import print_function

import os
import csv
import json
import time

from flask import Flask, request
from flask_restful import Resource, Api

from pymongo import MongoClient, GEO2D

DB_HOST = os.environ.get('DB_HOST', 'mongodb')
DB_NAME = os.environ.get('DB_NAME', 'mongodb')

DB_USERNAME = os.environ.get('DB_USERNAME', 'mongodb')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'mongodb')

DB_URI = 'mongodb://%s:%s@%s:27017/%s' % (DB_USERNAME, DB_PASSWORD,
        DB_HOST, DB_NAME)

DATASET_DATA = 'data.csv'

application = Flask(__name__)

api = Api(application)

with open('info.json') as fp:
    DATASET_INFO = json.load(fp)

client = MongoClient(DB_URI)
database = client[DB_NAME]
collection = database[DATASET_INFO['id']]

class Siege(Resource):
    def get(self):
        args = request.args

        duration = float(args.get('duration', '0.25'))

        end_time = time.time() + duration

        x = 123.456

        while time.time() < end_time:
            x**x

        return 'OK'

api.add_resource(Siege, '/ws/siege/')

class HealthCheck(Resource):
    def get(self):
        return 'OK'

api.add_resource(HealthCheck, '/ws/healthz/')

class Info(Resource):
    def get(self):
        return DATASET_INFO

api.add_resource(Info, '/ws/info/')

class DataLoad(Resource):
    def get(self):
        collection.remove({})
        collection.create_index([('Location', GEO2D)])

        with open(DATASET_DATA, 'rb') as fp:
            reader = csv.reader(fp)

            headers = reader.next()

            entries = []

            for row in reader:
                entry = dict(zip(headers, row))

                loc = [float(entry['Longitude']), float(entry['Latitude'])]
                entry['Location'] = loc

                entries.append(entry)

                if len(entries) >= 1000:
                    collection.insert_many(entries)
                    entries = []

            if entries:
                collection.insert_many(entries)

        return 'Inserted %s items.' % collection.count()

api.add_resource(DataLoad, '/ws/data/load')

def format_result(entries):
    result = []

    for entry in entries:
        data = {}

        data['name'] = entry['Name']
        data['latitude'] = entry['Latitude']
        data['longitude'] = entry['Longitude']

        result.append(data)

    return result

class DataAll(Resource):
    def get(self):
        return format_result(collection.find())

api.add_resource(DataAll, '/ws/data/all')

class DataWithin(Resource):
    def get(self):
        args = request.args

        box = [[float(args['lon1']), float(args['lat1'])],
               [float(args['lon2']), float(args['lat2'])]]

        query = {"Location": {"$within": {"$box": box}}}

        return format_result(collection.find(query))

api.add_resource(DataWithin, '/ws/data/within')
