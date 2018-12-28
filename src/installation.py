from flask import request;
from flask_restful import Resource
from Crypto.PublicKey import RSA
import github3
import os
import logging

class InstallationResource(Resource):
	def post(self):		
		payload = request.json
		if(payload['action'] == "created"):

			print("*********************")
			print(request.headers)
			install_id = payload['installation']['id']
			print("New install: " + str(install_id) )
			self.authenticate_app(install_id)
			print("*********************")

			self.update_repositories()



	def authenticate_app(self, install_id):
		print("authenticating for : " + app_identifier)
		gh = github3.GitHub()
		#client = gh.login_as_app(private_key_pem=key_file_pem, app_id=app_identifier)
		#print(client)
		gh.login_as_app_installation(private_key_pem=key_file_pem, app_id=app_identifier, installation_id=install_id)
		self.gh = gh
		
	def update_repositories(self):
		repos = self.gh.repositories()
		for repo in repos:
			print(repo)


webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
app_identifier=os.getenv("GITHUB_APP_IDENTIFIER")
private_key_path=os.getenv("GITHUB_PRIVATE_KEY")
key_file=open(private_key_path, "rb")
key_file_pem=key_file.read()
private_key=RSA.importKey(key_file_pem)