#!/bin/bash

# get 200, but no build
curl -X POST -d@test_files/pr_nolabel.form http://127.0.0.1:5000/check_for_label/allow -H "x_github_delivery:foo" -H "x_github_event:pull_request" -H "x_hub_signature:foo" -H "content-type:application/x-www-form-urlencoded"


# get 200 with build
curl -X POST -d@test_files/add_label.form http://127.0.0.1:5000/check_for_label/allow -H "x_github_delivery:foo" -H "x_github_event:pull_request" -H "x_hub_signature:foo" -H "content-type:application/x-www-form-urlencoded"