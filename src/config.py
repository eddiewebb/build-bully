from flask import request;
from flask_restful import Resource,reqparse
import github3
import os
import logging
import requests
import json

#oauth as user to edit stuff
#https://github.com/login/oauth/authorize?client_id=Iv1.12ce2c097c25f4d1&state=foooooooo&redirect_uri=https://bcacdf30.ngrok.io/oauth

class ConfigResource(Resource):


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
		return args['access_token'][0]



	def get_installations(self, token):
		update = requests.get('https://api.github.com/user/installations',
				headers = {
					"Accept":"application/vnd.github.machine-man-preview+json",
					"Authorization" : "token " + token
				}
			)
		print(update.text)
		update.raise_for_status()

