import flask
from flask import Flask, request, url_for, render_template, make_response
import googletrans
import flask_socketio
from flask_socketio import SocketIO, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

Users = []
sidMap = {}
uidMap = {}

class User:
    def __init__(self, username, sid, language, room, uid):
        self.username = username
        self.sid = sid
        self.language = language
        self.room = room
        self.uid = uid
        sidMap[sid] = self
        uidMap[uid] = self
        #only supposed to be in one room at a time, can change later

    def updateID(self, newID):
        oldID = self.sid
        self.sid = newID
        sidMap.pop(oldID)
        sidMap[newID] = self


@app.route('/')
def start():
    uid = str(uuid.uuid4()) #send a cookie with a unique UID to keep track of users on redirect
    cookie = make_response(render_template('index.html', uid=uid))
    cookie.set_cookie('id', uid)
    return cookie

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('newUser')
def registerUser(data):
    sid = request.sid
    user = data['u']
    if not user:
        user = "Anonymous"
    language = data['l']
    room = data['r']
    uid = data['id']
    newUser = User(user, sid, language, room, uid)
    Users.append(newUser)
    emit('redirect', url_for('chat'))

@socketio.on('update')
def updateID():
    User = uidMap.get(request.cookies.get('id'))
    User.updateID(request.sid)

@socketio.on('message')
def handleMessage(message):
    translator = googletrans.Translator()
    sender = sidMap[request.sid]
    senderName = sender.username
    room = sender.room
    output = ''
    for user in Users:
        if user.room == room:
            output = translator.translate(message, dest=user.language).text
            emit('message', senderName + ' : ' + output, room=user.sid)

if __name__ == '__main__':
    socketio.run(app)