from flask import request;
from flask_restful import Resource,reqparse
import github3
import os
import logging
import requests
import json
import urllib

#oauth as user to edit stuff
#https://github.com/login/oauth/authorize?client_id=Iv1.12ce2c097c25f4d1&state=foooooooo&redirect_uri=https://bcacdf30.ngrok.io/oauth

class ConfigResource(Resource):

	def get(self):		
		print("Oauth Request "  )
		print("*********************")
		print(request.headers)
		print("*********************")
		parser = reqparse.RequestParser()
		parser.add_argument('code')
		args = parser.parse_args()
		self.get_access_token(args['code'])

		# repo added, or webhook added/chanegd



	def get_access_token(self, code):
		payload={
			"client_id" : oauth_client_id,
			"client_secret": oauth_client_secret,
			"code" : code

		} 
		update = requests.post('https://github.com/login/oauth/access_token',
			headers = {
				"content-type" : "application/json"
			},
			data=json.dumps(payload))
		print(update.text)
		update.raise_for_status()
		args = urllib.parse.parse_qs(update.text)
		print(args['access_token'])
		



oauth_client_id=os.getenv("GITHUB_OAUTH_ID")
oauth_client_secret=os.getenv("GITHUB_OAUTH_SECRET")