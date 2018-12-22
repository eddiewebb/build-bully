from flask import Flask, request;
from flask_restful import Api, Resource
import requests
import json
import os


# Set environment Variables
secret = os.getenv("circleci_secret")
port = int(os.getenv("PORT","5000"))


def __main__():
	app = Flask(__name__)
	api = Api(app)

	# if they hit root, send index
	@app.route('/')
	def root():
	    return app.send_static_file('index.html')

	# soecific API endpiunts
	api.add_resource(WebHook,"/check_for_label/<string:tag_name>")

	app.run(debug=True, host='0.0.0.0', port=port)


class WebHook(Resource):
	def forward_if_valid(self, tag_name):
		# GitHub form-encoded data just wraps JSON in a "payload" form element.
		payload = json.loads(request.form['payload'])

		action = payload['action']
		if ( action not in ["synchronize","opened","labeled"] ):
			return self.send_to_circle()

		print("PR Based webhook, inspecting for label")

		# if our magic label was added, build it.
		if ( action == "labeled" and payload['label']['name'] == tag_name ):
			return self.send_to_circle()

		# otherwise, inpect existing labels
		allow_it = True
		try:
			is_forked = payload['pull_request']['head']['repo']['fork']
			if ( is_forked ):
				print( "Fork you!" )
				allow_it = False
				labels = payload['pull_request']['labels']
				for label in labels:
					if ( label['name'] == tag_name ):
						allow_it = True
						print("Found PR label with value: " + tag_name + ", will pass webhook along")
						break				

		except KeyError:
			print("Fork key not found, pass it along")

		if (allow_it):
			return self.send_to_circle()
		else:
			return 400


	def send_to_circle(self):
		print("Attempting to forward webhook to CircleCI...")

		#requests_session = requests.Session()
		#
		#  CircleCI only plays nice with application/x-www-form-urlencoded
		#
		response = requests.post(
			'https://circle.blueskygreenbuilds.com/hooks/github',
			headers={
				"Content-Type": "application/x-www-form-urlencoded",
				"X-GitHub-Delivery": request.headers["X-GitHub-Delivery"],
				"X-GitHub-Event": self.event,
				"X-Hub-Signature": request.headers["X-Hub-Signature"],
			},
			data=request.form,
			verify=False
		)
		print("Response from CIrcleCI:")
		print(response.status_code)
		response.raise_for_status()
		print("Success!")
		return response.status_code


	def post(self, tag_name):
		self.event =  request.headers["X-GitHub-Event"]
		# we only filter PRs, looking for unapproved forks
		if ( self.event == "pull_request" ):
			return self.forward_if_valid(tag_name)
		else:
			return self.send_to_circle()
		


__main__()