from flask import Flask, request;
from flask_restful import Api, Resource, reqparse
import requests
import json
import os
import pickle
from Crypto.PublicKey import RSA
import logging
import github3
import time
import jwt
import installation, webhook

# Set environment Variables
port = int(os.getenv("PORT","5000"))
webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET")
app_identifier=os.getenv("GITHUB_APP_IDENTIFIER")
private_key_path=os.getenv("GITHUB_PRIVATE_KEY")
key_file=open(private_key_path, "r")
key_file_pem=key_file.read()
private_key=RSA.importKey(key_file_pem)





logger = logging.getLogger()


def __main__():
	app = Flask(__name__)
	api = Api(app)

	# if they hit root, send index
	@app.route('/')
	def root():
	    return app.send_static_file('index.html')

	# soecific API endpiunts
	api.add_resource(webhook.WebhookResource,"/check_for_label/<string:tag_name>")
	api.add_resource(installation.InstallationResource,"/installation")

	app.run(debug=True,host='0.0.0.0', port=port)



def send_to_circle(site, webhook):
	response = requests.post(
		site + '/hooks/github',
		headers={
			"Content-Type": "application/x-www-form-urlencoded",
			"X-GitHub-Delivery": webhook.headers["X-GitHub-Delivery"],
			"X-GitHub-Event": webhook.headers["X-GitHub-Event"],
			"X-Hub-Signature": webhook.headers["X-Hub-Signature"],
		},
		data=webhook.form,
		verify=False
	)
	return response.status_code





#
# Load Flask and run app
#
__main__()