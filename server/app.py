from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    workout_schema, workouts_schema,
    exercise_schema, exercises_schema,
    workout_exercise_schema,
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


# ─────────────────────────────────────────────────────────────────────────────
#  WORKOUT ROUTES
# ─────────────────────────────────────────────────────────────────────────────

# ── GET /workouts ─────────────────────────────────────────────────────────────
@app.route('/workouts', methods=['GET'])
def get_workouts():
    """List all workouts."""
    workouts = Workout.query.order_by(Workout.date.desc()).all()
    return make_response(workouts_schema.dumps(workouts), 200, {'Content-Type': 'application/json'})


# ── GET /workouts/<id> ────────────────────────────────────────────────────────
@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    """
    Show a single workout with its associated exercises.
    Includes reps/sets/duration data from WorkoutExercises.
    """
    workout = Workout.query.get(id)
    if not workout:
        return make_response(
            jsonify({"error": f"Workout with id {id} not found."}), 404
        )
    return make_response(workout_schema.dumps(workout), 200, {'Content-Type': 'application/json'})


# ── POST /workouts ────────────────────────────────────────────────────────────
@app.route('/workouts', methods=['POST'])
def create_workout():
    """Create a new workout."""
    json_data = request.get_json()
    if not json_data:
        return make_response(jsonify({"error": "No input data provided."}), 400)

    try:
        data = workout_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return make_response(jsonify({"error": str(err)}), 422)

    return make_response(workout_schema.dumps(workout), 201, {'Content-Type': 'application/json'})


# ── DELETE /workouts/<id> ─────────────────────────────────────────────────────
@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    """
    Delete a workout.
    Associated WorkoutExercises are deleted via cascade.
    """
    workout = Workout.query.get(id)
    if not workout:
        return make_response(
            jsonify({"error": f"Workout with id {id} not found."}), 404
        )

    db.session.delete(workout)
    db.session.commit()
    return make_response(
        jsonify({"message": f"Workout (id={id}) deleted successfully."}), 200
    )


# ─────────────────────────────────────────────────────────────────────────────
#  EXERCISE ROUTES
# ─────────────────────────────────────────────────────────────────────────────

# ── GET /exercises ────────────────────────────────────────────────────────────
@app.route('/exercises', methods=['GET'])
def get_exercises():
    """List all exercises."""
    exercises = Exercise.query.order_by(Exercise.name).all()
    return make_response(exercises_schema.dumps(exercises), 200, {'Content-Type': 'application/json'})


# ── GET /exercises/<id> ───────────────────────────────────────────────────────
@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    """Show an exercise and its associated workouts."""
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(
            jsonify({"error": f"Exercise with id {id} not found."}), 404
        )
    return make_response(exercise_schema.dumps(exercise), 200, {'Content-Type': 'application/json'})


# ── POST /exercises ───────────────────────────────────────────────────────────
@app.route('/exercises', methods=['POST'])
def create_exercise():
    """Create a new exercise."""
    json_data = request.get_json()
    if not json_data:
        return make_response(jsonify({"error": "No input data provided."}), 400)

    try:
        data = exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return make_response(jsonify({"error": str(err)}), 422)
    except IntegrityError:
        db.session.rollback()
        return make_response(
            jsonify({"error": f"An exercise named '{data.get('name')}' already exists."}), 409
        )

    return make_response(exercise_schema.dumps(exercise), 201, {'Content-Type': 'application/json'})


# ── DELETE /exercises/<id> ────────────────────────────────────────────────────
@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    """
    Delete an exercise.
    Associated WorkoutExercises are deleted via cascade.
    """
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response(
            jsonify({"error": f"Exercise with id {id} not found."}), 404
        )

    db.session.delete(exercise)
    db.session.commit()
    return make_response(
        jsonify({"message": f"Exercise '{exercise.name}' deleted successfully."}), 200
    )


# ─────────────────────────────────────────────────────────────────────────────
#  WORKOUT EXERCISE ROUTE
# ─────────────────────────────────────────────────────────────────────────────

# ── POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises ──────
@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST']
)
def add_exercise_to_workout(workout_id, exercise_id):
    """
    Add an exercise to a workout, including reps/sets/duration.
    Requires at least one of: sets, duration_seconds.
    """
    workout = Workout.query.get(workout_id)
    if not workout:
        return make_response(
            jsonify({"error": f"Workout with id {workout_id} not found."}), 404
        )

    exercise = Exercise.query.get(exercise_id)
    if not exercise:
        return make_response(
            jsonify({"error": f"Exercise with id {exercise_id} not found."}), 404
        )

    json_data = request.get_json() or {}

    try:
        data = workout_exercise_schema.load(json_data)
    except ValidationError as err:
        return make_response(jsonify({"errors": err.messages}), 422)

    # Business rule: must provide sets or duration_seconds
    if not data.get("sets") and not data.get("duration_seconds"):
        return make_response(
            jsonify({
                "error": "Please provide either 'sets' (with optional 'reps') or 'duration_seconds'."
            }),
            422
        )

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get("reps"),
            sets=data.get("sets"),
            duration_seconds=data.get("duration_seconds"),
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return make_response(jsonify({"error": str(err)}), 422)
    except IntegrityError:
        db.session.rollback()
        return make_response(
            jsonify({
                "error": (
                    f"Exercise (id={exercise_id}) is already in "
                    f"Workout (id={workout_id})."
                )
            }),
            409
        )

    return make_response(
        workout_exercise_schema.dumps(workout_exercise), 201,
        {'Content-Type': 'application/json'}
    )


if __name__ == '__main__':
    app.run(port=5555, debug=True)
