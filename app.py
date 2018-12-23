from flask import Flask, request;
from flask_restful import Api, Resource, reqparse
import requests
import json
import os
import pickle


# Set environment Variables
port = int(os.getenv("PORT","5000"))


def __main__():
	app = Flask(__name__)
	api = Api(app)

	# if they hit root, send index
	@app.route('/')
	def root():
	    return app.send_static_file('index.html')

	# soecific API endpiunts
	api.add_resource(WebhookResource,"/check_for_label/<string:tag_name>")

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


class WebhookResource(Resource):
	def post(self, tag_name):
		parser = reqparse.RequestParser()
		parser.add_argument('site', default='https://circleci.com')
		args = parser.parse_args()
		self.webhook = Webhook(request.headers, request.form)
		self.site = args['site']
		print("Filtering '" + self.site + "' traffic for label '" + tag_name + "'")
		# we only filter PRs, looking for unapproved forks
		if ( self.webhook.is_forked and self.webhook.is_actionable()):
			return self.apply_filter_by_tag(tag_name)
		else:
			# let circle build local PRs, pushes, etc, or just ignore it. Point is we dont care about it.
			return send_to_circle(self.site, self.webhook)

	def apply_filter_by_tag(self, tag_name):		
		# if our magic label was added, send last attempt on this PR.
		if ( self.webhook.is_newly_labeled_with(tag_name) ):
			print("New label, attempt replay")
			return self.send_last_to_circle()

		if (self.is_label_set(tag_name)):
			print("Contains label, pass along")
			return send_to_circle(self.site, self.webhook)
		else:
			print("Not labled, save for future replay")
			self.webhook.to_file()
			return 200

	def is_label_set(self, label_name):
		for label in self.webhook.labels:
			if ( label['name'] == label_name ):
				print("Found PR label with value: " + label_name + ", will pass webhook along")
				return True	
		return False

	def send_last_to_circle(self):
		try:
			return send_to_circle(self.site, Webhook.from_file(self.webhook.pr_id))
		except FileNotFoundError:
			print("Previous webhook for newly labeled PR not found, no webhook to send.")
			return 200

class Webhook:
	def __init__(self, headers, form):
		# onlt headers and form are needed to send
		self.headers = {}
		self.headers['X-GitHub-Event'] 		= headers["X-GitHub-Event"]
		self.headers['X-GitHub-Delivery'] 	= headers["X-GitHub-Delivery"]
		self.headers['X-Hub-Signature'] 	= headers["X-Hub-Signature"]
		self.form 	 						= form		
		# convenience accessors for forked PR decisions
		if [ headers["X-GitHub-Event"] == 'pull_request' ]:
			self.payload = json.loads(self.form['payload'])
			self.is_forked = self.payload['pull_request']['head']['repo']['fork']
			self.action = self.payload['action']
			self.pr_id = self.payload['pull_request']['id']
			self.labels = self.payload['pull_request']['labels']
		else:
			self.is_forked = False

	def to_file(self):
		Webhook.write_file(str(self.pr_id) + '-headers.bin', self.headers)
		Webhook.write_file(str(self.pr_id) + '-form.bin', self.form)

	def is_newly_labeled_with(self, tag_name):
		return self.action == "labeled" and self.payload['label']['name'] == tag_name 

	def is_actionable(self):
		return self.action in ["synchronize","opened","reopened","labeled"] 

	@staticmethod
	def from_file(pr_id):
		headers = Webhook.read_file(str(pr_id) + '-headers.bin')
		form = Webhook.read_file(str(pr_id) + '-form.bin')
		return Webhook(headers, form)

	@staticmethod
	def read_file(file_name):		
		binary_file = open(file_name, mode='rb')
		contents = pickle.load(binary_file)
		binary_file.close()
		os.remove(file_name)
		return contents

	@staticmethod
	def write_file(file_name,contents):	
		binary_file = open(file_name, mode='wb')
		pickle.dump(contents, binary_file)
		binary_file.close()


#
# Load Flask and run app
#
__main__()