from flask import Flask, request, render_template, session, flash, redirect, url_for
from flask_restful import Api, Resource, reqparse
import requests
import json
import os

import urllib
from src import installation, webhook, config

# Set environment Variables
port = int(os.getenv("PORT","5000"))
oauth_client_id=os.getenv("GITHUB_OAUTH_ID")
oauth_client_secret=os.getenv("GITHUB_OAUTH_SECRET")


def __main__():
	app = Flask(__name__)
	app.secret_key = b'_5#ibuzftngcabefdj#$%^&*gfxzrc]/'
	api = Api(app)

	# if they hit root, send index
	@app.route('/')
	def root():
	    return app.send_static_file('index.html')

	@app.route('/setup')
	def setup():
		if 'access_token' in session:
			name = "Known User"
		else:
			# not authed, not attempting, show them login
			name = None
		return render_template('setup.html', name=name)

	@app.route('/oauth')
	def login():
		app.logger.debug('Attempt oauth dance')
		try:			
			session['access_token'] = get_access_token(request.args.get('code'))
			flash('Login Successful')
			app.logger.debug('Success!')
		except Exception as e:
			app.logger.warn('OAuth attempt failed with error')
			app.logger.warn(e)
			flash('You must login from this page')

		return redirect(url_for('setup'))

	def get_access_token(code):
		payload={
			"client_id" : oauth_client_id,
			"client_secret": oauth_client_secret,
			"code" : code
		} 
		headers = {
				"content-type" : "application/json"
		}
		update = requests.post(
				'https://github.com/login/oauth/access_token',
				headers=headers,
				data=json.dumps(payload)
			)
		update.raise_for_status()
		args = urllib.parse.parse_qs(update.text)
		return args['access_token'][0]

	# "dumb" webhook endpoint uses the url and payload to decide if it drops or forwards
	api.add_resource(webhook.WebhookResource,"/check_for_label/<string:tag_name>")

	# authenticated endpoints to configure rules, webhooks, etc.  These probably are 1 endpoint.
	api.add_resource(installation.InstallationResource,"/installation")
	api.add_resource(config.ConfigResource,"/config")

	app.run(debug=True,host='0.0.0.0', port=port)








#
# Load Flask and run app
#
__main__()