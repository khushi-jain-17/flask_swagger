from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime 


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///databse.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

SWAGGER_URL ='/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config = {
        'app_name':"Todo List API"
    }
)

app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

db = SQLAlchemy(app)
ma = Marshmallow(app)


class TodoList(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(300),nullable=False)
    completed = db.Column(db.Boolean,nullable=False, default=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class TodoListSchema(ma.Schema):
    class Meta:
        fields= ('id','name','description','completed','date_created')


# instantiate schema objects for todolist and todolists
todolist_schema = TodoListSchema(many=False)
todolists_schema = TodoListSchema(many=True)


@app.errorhandler(400)
def handle_400_error(_error):
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@app.errorhandler(401)
def handle_401_error(_error):
    return make_response(jsonify({'error': 'Unauthorized'}), 401)


@app.errorhandler(404)
def handle_404_error(_error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    return make_response(jsonify({'error': 'Internal Server error'}), 500)


@app.route("/todolist", methods = ["POST"])
def add_todo():
    try:
        name = request.json['name']
        description = request.json['description']
        new_todo = TodoList(name=name, description=description)
        db.session.add(new_todo)
        db.session.commit()
        return todolist_schema.jsonify(new_todo)
    except Exception as e:
        return jsonify({"Error": "Invalid Request, please try again."})
        

@app.route("/todolist", methods = ["GET"])
def get_todos():
    todos = TodoList.query.all()
    result_set = todolists_schema.dump(todos)
    return jsonify(result_set)


@app.route("/todolist/<int:id>", methods=["GET"])
def get_todo(id):
    todo = TodoList.query.get_or_404(int(id))
    return todolist_schema.jsonify(todo)


@app.route("/todolist/<int:id>", methods=["PUT"])
def update_todo(id):
    todo = TodoList.query.get_or_404(int(id))
    try:
        name = request.json['name']
        description = request.json['description']
        completed = request.json['completed']
        todo.name = name
        todo.description = description
        todo.completed = completed
        db.session.commit()
    except Exception as e:
        return jsonify({"Error": "Invalid request, please try again."})
    return todolist_schema.jsonify(todo)


@app.route("/todolist/<int:id>", methods=["DELETE"])
def delete_todo(id):
    todo = TodoList.query.get_or_404(int(id))
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"Success" : "Todo deleted."})



if __name__ == "__main__":
    app.run(debug=True)
