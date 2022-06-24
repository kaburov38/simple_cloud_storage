from http import cookies
from math import comb
from urllib import response
from nameko.web.handlers import http
from requests import session
from werkzeug.wrappers import Response
import uuid
import json
from nameko.rpc import RpcProxy
import hashlib
from datetime import datetime

from gateway.dependencies.session import SessionProvider

def hash_file_name(file_name, salt):
    pepper = "ndak"
    return hashlib.sha256(file_name.encode() + pepper.encode() + salt.encode()).hexdigest()

class Service:
    name="gateway_service"

    session_provider = SessionProvider()
    account_rpc = RpcProxy('account_service')
    storage_rpc = RpcProxy('storage_service')

    @http('POST', '/register')
    def register(self, request):
        register_info = json.loads(request.get_data())
        username = register_info['username']
        password = register_info['password']
        if(self.account_rpc.register(username, password)):
            user_data = {
                'username': username
            }
            session_id = self.session_provider.set_session(user_data)
            response = Response('Register Success')
            response.set_cookie('SESSID', session_id)
            return response
        else:
            return Response('Username already exist')

    @http('POST', '/login')
    def login(self, request):
        login_info = json.loads(request.get_data())
        username = login_info['username']
        password = login_info['password']
        if(self.account_rpc.login(username, password)):
            user_data = {
                'username': username
            }
            session_id = self.session_provider.set_session(user_data)
            response = Response('Login Success')
            response.set_cookie('SESSID', session_id)
            return response
        else:
            return Response('Username or Password is wrong')
    
    @http('POST', '/upload')
    def upload(self, request):
        cookies = request.cookies
        if(cookies):
            session_id = cookies['SESSID']
            if(session_id):
                session_data = self.session_provider.get_session(session_id)
                if(session_data):
                    username = session_data['username']
                    file = request.files['file']
                    hash_name = username + str(datetime.now())
                    salt = str(uuid.uuid4())
                    hash_name = hash_file_name(hash_name, salt)
                    real_name = file.filename
                    ext = real_name.split('.')[-1]
                    hash_name += '.' + ext
                    file_path = './storage/'+ hash_name
                    if(self.account_rpc.is_username_exist(username)):
                        with open(file_path, 'wb') as f:
                            f.write(file.read())
                        self.storage_rpc.upload(username, hash_name, real_name)
                        return Response('Upload Success')
                    else:
                        return Response('Username Does Not Exist')
                else:
                    return Response('You need to Login First')
            else:
                return Response('You need to Login First')
        else:
            return Response('You need to Login First')

    @http('GET', '/download/<string:filename>')
    def download(self, request, filename):
        cookies = request.cookies
        if(cookies):
            session_id = cookies['SESSID']
            if(session_id):
                session_data = self.session_provider.get_session(session_id)
                if(session_data):
                    username = session_data['username']
                    hash_name = self.storage_rpc.download(username, filename)
                    if(hash_name):
                        file_path = './storage/'+ hash_name
                        with open(file_path, 'rb') as f:
                            response = Response(f.read(), mimetype='application/octet-stream')
                            response.headers['Content-Disposition'] = 'attachment; filename=' + filename
                            return response
                    else:
                        return Response('File Not Found')
                else:
                    return Response('You need to Login First')
            else:
                return Response('You need to Login First')
        else:
            return Response('You need to Login First')

    @http('GET', '/logout')
    def logout(self, request):
        cookies = request.cookies
        if(cookies):
            self.session_provider.delete(request.cookies.get('SESSID'))
            response = Response('Logout Success')
            response.delete_cookie('SESSID')
            return response
        else:
            return Response('You need to Login First')
