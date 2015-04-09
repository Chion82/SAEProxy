from flask import Flask, request, jsonify
import sae
import time
import random
import socket
import base64
import threading
from sae import channel

hosts = {}
ports = {}
message_to_send = {}

app = Flask(__name__)
app.debug = True

@app.route('/connect')
def connect():
	channelName = str(int(time.time())) + str(random.randint(100000,999999))
	url = channel.create_channel(channelName)
	host = request.args.get('host','')
	port = request.args.get('port','')
	if (url!='' and url!=None and host!='' and host!=None and port!='' and port!=None):
		hosts[channelName] = host
		ports[channelName] = int(port)
		return jsonify({'status':'OK','url':url})
	else:
		return jsonify({'status':'error'})

def sock_loop_recv(sock, channelName):
	try:
		while (channelName in hosts):
			data = sock.recv(1024)
			channel.send_message(channelName, base64.b64encode(data))
		sock.close()
	except exception, e:
		print(e)

def sock_loop_send(sock, channelName):
	try:
		while (channelName in hosts):
			if (channelName in message_to_send):
				raw_data_to_send = base64.b64decode(message_to_send[channelName])
				sock.send(raw_data_to_send)
				del message_to_send[channelName]
		sock.close()
	except exception, e:
		print(e)

@app.route('/_sae/channel/connected')
def on_connect():
	channelName = request.form['from']
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((hosts[channelName], ports[channelName]))
		threading.Thread(target=sock_loop_recv,args=(s,channelName)).start()
		threading.Thread(target=sock_loop_send,args=(s,channelName)).start()
		return jsonify({'status':'OK'})
	except exception, e:
		return jsonify({'status':'error','message':e})

@app.route('/_sae/channel/disconnected')
def on_disconnect():
	channelName = request.form['from']
	try:
		del hosts[channelName]
		del ports[channelName]
	except exception, e:
		return jsonify({'status':'Channel name not found.'})
	return jsonify({'status':'OK'})

@app.route('/_sae/channel/message')
def on_receive():
	channelName = request.form['from']
	message_to_send[channelName] = request.form['message']
	return jsonify({'status':'OK'})
