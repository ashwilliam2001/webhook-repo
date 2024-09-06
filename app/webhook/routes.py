from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import json
import pytz
from pymongo import MongoClient
from app.extensions import *

app_instance = Flask(__name__)
CORS(app_instance)


def format_timestamp(input_timestamp):
    if isinstance(input_timestamp, int):
        utc_time = datetime.utcfromtimestamp(input_timestamp)
    elif isinstance(input_timestamp, str):
        utc_time = datetime.strptime(input_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    else:
        return f"{input_timestamp}"

    formatted_time = utc_time.strftime('%d %B %Y - %I:%M %p UTC')
    day = utc_time.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    return utc_time.strftime(f'{day}{suffix} %B %Y - %I:%M %p UTC')

def print_webhook_message(message):
    print(f"\n{message}\n")


# Function to insert data into MongoDB
def insert_into_mongo(data):
    result = collection.insert_one(data)
    print(f"Document inserted with _id: {result.inserted_id}")


@app_instance.route('/requests', methods=['GET'])
def get_requests():
    requests = list(collection.find({}, {'_id': 0}))
    return jsonify(requests)


@app_instance.route("/", methods=["POST"])
def read_root():
    if request.headers['Content-Type'] == 'application/json':
        info = request.json
        # print(f"\n\n{json.dumps(info, indent=4)}\n\n")

        if 'pull_request' in info:
            
            author_name = info['pull_request']['user']['login']
            from_branch = info['pull_request']['head']['ref']
            to_branch = info['pull_request']['base']['ref']
            action_time = format_timestamp(info['pull_request']['updated_at'])

            if info['action'] == 'opened': # PR Opened
                """
                    Format: {author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
                    Sample: "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC
                """
                print_webhook_message(f'"{author_name}" submitted a pull request from "{from_branch}" to "{to_branch}" on {action_time}')
                mongo_data = {
                    "request_id": info['pull_request']['id'],
                    "author": author_name,
                    "action": "PULL_REQUEST",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": action_time
                }
                insert_into_mongo(mongo_data)

            elif info['action'] == 'closed': # PR Merged
                """
                    Format: {author} merged branch {from_branch} to {to_branch} on {timestamp}
                    Sample: "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC
                """
                print_webhook_message(f'"{author_name}" merged branch "{from_branch}" to "{to_branch}" on {action_time}')

                mongo_data = {
                    "request_id": info['pull_request']['id'],
                    "author": author_name,
                    "action": "MERGE",
                    "from_branch": from_branch,
                    "to_branch": to_branch,
                    "timestamp": action_time
                }
                insert_into_mongo(mongo_data)
                
        else: # 'push' event
            """
                Format: {author} pushed to {to_branch} on {timestamp}
                Sample: "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC
            """
            
            branch_name = info['ref'].split('/')[-1]
            push_time = format_timestamp(info['repository']['pushed_at'])

            for commit in info['commits']:
                print_webhook_message(f'"{commit["author"]["name"]}" pushed to "{branch_name}" on {push_time}')

                mongo_data = {
                    "request_id": commit['id'],
                    "author": commit['author']['name'],
                    "action": "PUSH",
                    "from_branch": branch_name,
                    "to_branch": branch_name,
                    "timestamp": push_time
                }
                insert_into_mongo(mongo_data)
                
        return jsonify(info)

