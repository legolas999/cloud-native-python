#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask import abort
from flask import make_response
import json
import sqlite3


app = Flask(__name__)

def list_users():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully");
    api_list=[]
    cursor = conn.execute("SELECT username,full_name,emailid,password,id from users")
    for row in cursor:
        a_dict = {}
        a_dict['username'] = row[0]
        a_dict['name'] = row[1]
        a_dict['email'] = row[2]
        a_dict['password'] = row[3]
        a_dict['id'] = row[4]
        api_list.append(a_dict)
    conn.close()
    return jsonify({'user_list': api_list})

def list_user(user_id):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully");
    api_list=[]
    cursor = conn.cursor()
    cursor.execute("SELECT * from users where id=?",(user_id,))
    data = cursor.fetchall()
    print(data)
    if len(data) == 0:
        abort(404)
    else:
        user = {}
        user['username'] = data[0][0]
        user['email'] = data[0][1]
        user['password'] = data[0][2]
        user['name'] = data[0][3]
        user['id'] = data[0][4]
    conn.close()
    return jsonify(user)

def add_user(new_user):
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully");
    #api_list=[]
    cursor=conn.cursor()
    cursor.execute("SELECT * from users where username=? or emailid=?",(new_user['username'],new_user['emailid']))
    data = cursor.fetchall()
    if len(data) != 0:
        abort(409)
    else:
        cursor.execute("insert into users (username,emailid,password,full_name) values(?,?,?,?)",(new_user['username'],new_user['emailid'],new_user['password'],new_user['name']))
        conn.commit()
        return "Success"
    conn.close()
    #return jsonify(a_dict)


@app.route("/api/v1/info")
def home_index():
    conn = sqlite3.connect('mydb.db')
    print("Opened database successfully");
    api_list=[]
    cursor = conn.execute("SELECT buildtime,version,methods,links from apirelease")
    for row in cursor:
        api = {}
        api['version'] = row[1]
        api['buildtime'] = row[0]
        api['methods'] = row[2]
        api['links'] = row[3]
        api_list.append(api)
    conn.close()
    return jsonify({'api_version': api_list}), 200

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return list_users()

@app.route('/api/v1/users/<int:user_id>',methods=['GET'])
def get_user(user_id):
    return list_user(user_id)

@app.route('/api/v1/users',methods=['POST'])
def create_user():
    if not request.json or not 'username' in request.json or not 'email' in request.json or not 'password' in request.json:
        abort(400)
    user = {
        'username': request.json['username'],
        'emailid':  request.json['email'],
        'name': request.json.get('name',""),
        'password': request.json['password']
    }
    return jsonify({'status': add_user(user)}), 201



@app.errorhandler(404)
def resource_not_found(error):
    return make_response(jsonify({'error': 'Resource not found!'}), 404)

@app.errorhandler(400)
def invalid_request(error):
    return make_response(jsonify({'error':'Bad Request'}), 400)

@app.errorhandler(409)
def user_found(error):
    return make_response(jsonify({'error':'Conflict! Record exist'}), 409)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
