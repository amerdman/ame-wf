#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
import webapp2
import guestbook

import os
from google.appengine.ext.webapp import template
from google.appengine.ext import db

class MainHandler(webapp2.RequestHandler):
	def get(self):
		bikerJs = "["
		for biker in db.GqlQuery("SELECT * FROM Biker"):
			bikerJs += "{lat:'" + biker.lat + "',lon:'" + biker.lon + "',name:'" + biker.biker_name + "'},"

		bikerJs = bikerJs.rstrip(",") + "]"

		busJs = '{}'
		bus = db.GqlQuery("SELECT * FROM Bus ORDER BY last_checkin DESC").get()
		if bus is not None:
			busJs = "{ lat:'" + bus.lat + "',lon:'" + bus.lon + "'}"
			
		template_values = {'actionArea':self.getActionArea(), 'busLocation':busJs, 'bikerLocations':bikerJs}
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

	# method to retrieve the action area of the main template
	def getActionArea(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/bikerActionArea.html')
		return template.render(path, {})

	# method to catch postbacks, only meant for ajax requests
	def post(self):
		biker = Biker()
		biker.lat = self.request.get('lat')
		biker.lon = self.request.get('lon')
		biker.biker_name = self.request.get('name')
		biker.put()
		self.response.out.write('success')

class BusdriverHandler(MainHandler):
	# overwrites base method to load action area template for bus driver
	def getActionArea(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/busdriverActionArea.html')
		return template.render(path, {})

	# overwrites base method to catch postbacks, save bus location
	def post(self):
		bus = Bus()
		bus.lat = self.request.get('lat')
		bus.lon = self.request.get('lon')
		bus.directions = self.request.get('directions')
		bus.put()
		self.response.out.write('success')
		

class Biker(db.Model):
	lat = db.StringProperty()
	lon = db.StringProperty()
	biker_name = db.StringProperty()
	last_checkin = db.DateTimeProperty(auto_now_add=True)

class Bus(db.Model):
	lat = db.StringProperty()
	lon = db.StringProperty()
	directions = db.StringProperty()
	last_checkin = db.DateTimeProperty(auto_now_add=True)

# initialize the main app
app = webapp2.WSGIApplication([
    ('/guestbook/', guestbook.GuestbookMainPage),
    ('/guestbook', guestbook.GuestbookMainPage),
    ('/guestbook/sign', guestbook.GuestbookSign),
    ('/busdriver', BusdriverHandler),
    ('/', MainHandler)
], debug=True)
