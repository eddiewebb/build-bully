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
		if(request.headers["X-GitHub-Event"] == 'installation' and payload['action'] == "created"):
			install_id = payload['installation']['id']
			print("New install: " + str(install_id) )
			print("*********************")
			print(request.headers)
			self.authenticate_app(install_id)
			print("*********************")
			self.update_webhooks(action="bully")
		elif(payload['action'] == "deleted"):
			install_id = payload['installation']['id']
			print("Removed install: " + str(install_id) )


		# repo added, or webhook added/chanegd



	def authenticate_app(self, install_id):
		gh = github3.GitHub()
		gh.login_as_app_installation(key_file_pem, app_identifier, install_id)
		self.gh = gh
		self.access_token = gh.session.auth.token
		#print(gh.session.auth.__dict__)
		
	def update_webhooks(self, action):
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
				if( action == 'bully' and w_url == circleci_url ):
					patch = '{"config": {"url":"' + bully_url + '"}'
					patch_webhook(patch)
					print("Bullied Circle Config")
				elif( action == 'release' and w_url == bully_url ):
					patch = '{"config": {"url":"' + circleci_url + '"}'
					patch_webhook(patch)
					print("released repo")
				else:
					print("not CIrcle CI hhook")

	def patch_webhook(self, patch):
		update = requests.patch('https://api.github.com/repos/' + repo ['full_name'] + '/hooks/' + str(hook['id']),
			headers = {
				"Authorization" : 'token ' + self.access_token,
				"content-type" : "application/json"
			},
			data=patch)
		print(update.text)
		update.raise_for_status()


circleci_url='https://circleci.com/hooks/github'
bully_url='http://buildbully.cfapp.io/check_for_label/allow'



webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
app_identifier=os.getenv("GITHUB_APP_IDENTIFIER")
private_key_path=os.getenv("GITHUB_PRIVATE_KEY")
key_file=open(private_key_path, "rb")
key_file_pem=key_file.read()