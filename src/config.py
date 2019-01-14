from flask import request;
from flask_restful import Resource,reqparse
import github3
import requests
import json

class ConfigResource(Resource):
	def get_installations(self, token):
		update = requests.get('https://api.github.com/user/installations',
				headers = {
					"Accept":"application/vnd.github.machine-man-preview+json",
					"Authorization" : "token " + token
				}
			)
		print(update.text)
		update.raise_for_status()

