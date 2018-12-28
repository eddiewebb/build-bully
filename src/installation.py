from flask import request;
from flask_restful import Resource
from Crypto.PublicKey import RSA
import github3
import time
import jwt
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
			auth = self.authenticate_app(install_id)
			print(auth)
			print("*********************")




	def authenticate_app(self, install_id):
		print("authenticating for : " + app_identifier)
		payload = {
		  # The time that this JWT was issued, _i.e._ now.
		  "iat": time.time(),

		  # JWT expiration time (10 minute maximum)
		  "exp": time.time() + (10 * 60),

		  # Your GitHub App's identifier number
		  "iss": app_identifier
		}

		# Cryptographically sign the JWT
		jwt_token = jwt.encode(payload, key_file_pem, algorithm='RS256')

		# Create the App client, using the JWT as the auth token, this wil let us create install specific tokens
		client = github3.login(token=jwt_token)
		print(client.__dict__.keys())
		#@app_client ||= Octokit::Client.new(bearer_token: jwt)
		print(client.apps)
		client.app_installaton(install_id)

		# install specific client		
		client = github3.login(token=jwt_token)
		return auth
		


webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
app_identifier=os.getenv("GITHUB_APP_IDENTIFIER")
private_key_path=os.getenv("GITHUB_PRIVATE_KEY")
key_file=open(private_key_path, "r")
key_file_pem=key_file.read()
private_key=RSA.importKey(key_file_pem)