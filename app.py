from flask import Flask, request;
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)



class WebHook(Resource):
	def forward_if_valid(self, payload, tag_name):
		print("You contributed via  a PR")


		try:
			is_forked = payload['pull_request']['head']['repo']['fork']
			if ( is_forked ):
				print( "Fork you!" )
		except KeyError:
			print("Fork key not found, pass it along")

	def dont_care(self, payload):
		print("You did stuff we dont care about")


	def post(self, tag_name):
		payload = request.get_json(force=True)
		action = payload['action']

		if (action in ["synchronize","opened"]):
			self.forward_if_valid(payload, tag_name)
		else:
			self.dont_care(payload)

		return 200

api.add_resource(WebHook,"/check_for_label/<string:tag_name>")


app.run(debug=True)

# if action is "opened", than "labels" areinclued under "pull_rquest" https://github.com/cci-training/test-repo/settings/hooks/33724084


# subsequet pushes trgger a "action": "synchronize", nd includes the same



# pull_request.head.repo.fork indicates if source repo was forked