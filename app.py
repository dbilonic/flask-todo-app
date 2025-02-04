from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
import os

app = Flask(__name__)

# PostgreSQL Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///todo.db")
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Cache Configuration
app.config["CACHE_TYPE"] = "simple"  # Use in-memory cache
app.config["CACHE_DEFAULT_TIMEOUT"] = 60  # Cache timeout (in seconds)
cache = Cache(app)

db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# Cache the homepage for 60 seconds
@cache.cached(timeout=60)
@app.route("/")
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    task_content = request.form["content"]
    if task_content:
        new_task = Task(content=task_content)
        db.session.add(new_task)
        db.session.commit()
        cache.clear()  # Clear cache after adding a task
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        cache.clear()  # Clear cache after deleting a task
    return redirect(url_for("index"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = not task.completed
        db.session.commit()
        cache.clear()  # Clear cache after completing a task
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
