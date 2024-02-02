from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={ r"/users/*": {"origins": ["http://127.0.0.1:4000", "https://austinzhang1.github.io"]},
    r"/login/*": {"origins": ["http://127.0.0.1:4000", "https://austinzhang1.github.io"]},
    r"/users": {"origins": ["http://127.0.0.1:4000", "https://austinzhang1.github.io"]}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file named users.db
db = SQLAlchemy(app)
api = Api(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password
        }

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([user.serialize() for user in users])
    
    def post(self):
        data = request.get_json()
        print("Received data:", data)  # Add this line for debugging
        new_user = User(username=data['username'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.serialize())


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return jsonify(user.serialize())

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return jsonify({"message": "Login successful"})
        else:
            return jsonify({"message": "Login failed"}), 401

api.add_resource(UserListResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(LoginResource, '/authenticate')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)