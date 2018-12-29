from flask import request;
from flask_restful import Resource
import github3
import os
import logging
import requests
import json

class InstallationResource(Resource):
	def post(self):		
		payload = request.json
		if(payload['action'] == "created"):
			install_id = payload['installation']['id']
			print("New install: " + str(install_id) )
			print("*********************")
			print(request.headers)
			self.authenticate_app(install_id)
			print("*********************")
			self.update_webhooks()



	def authenticate_app(self, install_id):
		gh = github3.GitHub()
		gh.login_as_app_installation(key_file_pem, app_identifier, install_id)
		self.gh = gh
		self.access_token = gh.session.auth.token
		#print(gh.session.auth.__dict__)
		
	def update_webhooks(self):
		response = requests.get('https://api.github.com/installation/repositories',
			headers = {
				"Authorization" : 'token ' + self.access_token,
				"Accept": 'application/vnd.github.machine-man-preview+json'
			})
	
		response.raise_for_status()
		repositories = response.json()['repositories']
		for repo in repositories:
			print(repo['name'])
			hook_r = requests.get('https://api.github.com/repos/' + repo ['full_name'] + '/hooks',
				headers = {
					"Authorization" : 'token ' + self.access_token,
					"Accept": 'application/vnd.github.machine-man-preview+json'
				})
		
			hook_r.raise_for_status()
			webhooks = hook_r.json()
			for hook in webhooks:
				w_url=hook['config']['url']
				if( w_url == 'https://circleci.com/hooks/github'):
					patch = '{"config": {"url":"http://buildbully.cfapp.io/check_for_label/allow"}'
					update = requests.patch('https://api.github.com/repos/' + repo ['full_name'] + '/hooks/' + str(hook['id']),
						headers = {
							"Authorization" : 'token ' + self.access_token,
							"content-type" : "application/json"
						},
						data=patch)
					print(update.text)
					update.raise_for_status()
					print("Bullied Circle Config")
				elif( w_url == 'http://buildbully.cfapp.io/check_for_label/allow'):
					print("already bullied")
				else:
					print("not CIrcle CI hhook")
				



		



webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
app_identifier=os.getenv("GITHUB_APP_IDENTIFIER")
private_key_path=os.getenv("GITHUB_PRIVATE_KEY")
key_file=open(private_key_path, "rb")
key_file_pem=key_file.read()