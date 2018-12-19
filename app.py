from flask import Flask, request;
from flask_restful import Api, Resource
import requests
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
	def forward_if_valid(self, payload, tag_name):
		# default to allow it.
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
			return self.pass_it_along(payload)
		else:
			return 400


	def pass_it_along(self, payload):
		print("Attempting to sent to CircleCI")
		print("payload:")
		print(payload)

		#requests_session = requests.Session()
		response = requests.post(
			'https://circleci.com/hooks/github',
			headers={
				"Content-Type": "application/json",
				"X-GitHub-Delivery": request.headers["X-GitHub-Delivery"],
				"X-GitHub-Event": request.headers["X-GitHub-Event"],
				"X-Hub-Signature": request.headers["X-Hub-Signature"],
			},
			data=payload,
			verify=False
		)
		print("Response from CIrcleCI:")
		print(response.status_code)
		print(response.text)
		response.raise_for_status()
		return response


	def post(self, tag_name):
		payload = request.get_json(force=True)
		action = payload['action']

		if (action in ["synchronize","opened"]):
			self.forward_if_valid(payload, tag_name)
		else:
			self.pass_it_along(payload)

		return 200


__main__()