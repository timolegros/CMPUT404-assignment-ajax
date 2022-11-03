#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request
import json

app = Flask(__name__)
app.debug = True


# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        self.entity_id_counter = 0

    # only useful if we have a PATCH method, but we don't
    def update(self, entity_id, key, value):
        entry = self.space.get(entity_id, dict())
        entry[key] = value
        self.space[entity_id] = entry

    def replace(self, entity_id, data):
        self.space[entity_id] = data

    def create(self, data):
        self.space[self.entity_id_counter] = data
        self.entity_id_counter += 1
        return self.entity_id_counter

    def clear(self):
        self.space = dict()
        self.entity_id_counter = 0

    def get(self, entity_id):
        return self.space.get(entity_id, dict())

    def world(self):
        return self.space


# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()


# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])


def validate_entity(entity):
    if 'x' not in entity:
        return False
    if 'y' not in entity:
        return False
    if 'colour' not in entity:
        return False

    return True


@app.route("/")
def hello():
    """redirect to /static/index.html"""
    return app.send_static_file("index.html")


# This assumes a client can modify the entity of another client
@app.route("/entity/<entity_id>", methods=['PUT'])
def update(entity_id):
    """update the entities via this interface"""
    if validate_entity(request.json):
        myWorld.replace(entity_id, request.json)
        return json.dumps({'status': 'success'})
    else:
        return flask.Response(json.dumps({'status': 'The given entity must include x, y, and colour'}), status=400,
                              mimetype='application/json')


# POST cannot have a route of /entity/<entity> because using a client generated id could cause collisions
# i.e. what is 2 different clients POST different entities with the same id -> race condition
@app.route('/entity', methods=['POST'])
def create():
    return str(myWorld.create(request.json))


@app.route("/world", methods=['POST', 'GET'])
def world():
    """you should probably return the world here"""
    if request.method == 'GET':
        return json.dumps(myWorld.world())
    else:
        return None


@app.route("/entity/<entity_id>")
def get_entity(entity_id):
    """This is the GET version of the entity interface, return a representation of the entity"""
    return json.dumps(myWorld.get(entity_id))


@app.route("/clear", methods=['POST', 'GET'])
def clear():
    """Clear the world out!"""
    myWorld.clear()
    return json.dumps({'status': 'Success'})


if __name__ == "__main__":
    app.run()
