from flask import Flask, request, Response
import requests
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
  return Response("", status=200, mimetype="application/json")

@app.route('/', methods=['POST'])
def post():
  data = request.json
  if not(checker(data)):
    return Response("", status=200, mimetype="application/json")


  data = data['data']['statementItem']
  comment = None
  if 'comment' in data:
    comment = data['comment']

  user = asyncio.run(get_user(comment))
  payment = float(data['amount']) / 100
  
  if (user == None):
    asyncio.run(create_transaction(None, payment))
    return Response("", status=200, mimetype="application/json")

  sum = float(user['balance']) + payment
  asyncio.run(update_user(comment, sum))
  asyncio.run(create_transaction(user['id'], payment))
    

  return Response("", status=200, mimetype="application/json")

async def create_transaction(id, sum):
  url = os.getenv('SUPABASE_URL') + 'rest/v1/transactions'
  headers={
    "apikey": os.getenv('SUPABASE_KEY')
  }
  data = {
    "desc": "Поповнення балансу",
    "sum": sum,
    "user": id
  }
  requests.post(url, headers=headers, json=data)

async def update_user(id, sum):
  url = os.getenv('SUPABASE_URL') + 'rest/v1/users?telegram=eq.' + id
  headers={
    "apikey": os.getenv('SUPABASE_KEY')
  }
  data = {
    "balance": sum
  }
  requests.patch(url, headers=headers, json=data)

async def get_user(id):
  if (id == None):
    return None
  url = os.getenv('SUPABASE_URL') + 'rest/v1/users?telegram=eq.' + id
  headers={
    "apikey": os.getenv('SUPABASE_KEY')
  }
  user = requests.get(url, headers=headers)
  if(len(user.json()) > 0):
    return user.json()[0]
  return None

def checker(data):
  if not('type' in data):
    return False
  
  if data['type'] != 'StatementItem':
    return False

  if not('data' in data):
    return False

  if not('statementItem' in data['data']):
    return False
  return True

if __name__ == "__main__":
  app.run(debug=True, port=5000)