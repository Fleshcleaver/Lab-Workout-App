from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


# ── Exercise ──────────────────────────────────────────────────────────────────
class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout", secondary="workout_exercises", back_populates="exercises", viewonly=True
    )

    # ── Model Validations ─────────────────────────────────────────────────────
    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be empty.")
        if len(value) > 100:
            raise ValueError("Exercise name cannot exceed 100 characters.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        valid_categories = [
            "strength", "cardio", "flexibility",
            "balance", "plyometrics", "sports", "other"
        ]
        if not value or not value.strip():
            raise ValueError("Category is required.")
        if value.lower().strip() not in valid_categories:
            raise ValueError(
                f"Category must be one of: {', '.join(valid_categories)}."
            )
        return value.lower().strip()

    def __repr__(self):
        return (
            f"<Exercise id={self.id} name='{self.name}' "
            f"category='{self.category}' equipment={self.equipment_needed}>"
        )


# ── Workout ───────────────────────────────────────────────────────────────────
class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise", secondary="workout_exercises", back_populates="workouts", viewonly=True
    )

    # ── Model Validations ─────────────────────────────────────────────────────
    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None:
            raise ValueError("Duration is required.")
        if not isinstance(value, int) or value < 1:
            raise ValueError("Duration must be a positive integer (in minutes).")
        if value > 480:
            raise ValueError("Duration cannot exceed 480 minutes (8 hours).")
        return value

    @validates("date")
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Date is required.")
        return value

    def __repr__(self):
        return (
            f"<Workout id={self.id} date={self.date} "
            f"duration={self.duration_minutes}min>"
        )


# ── WorkoutExercise (Join Table) ──────────────────────────────────────────────
class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer, db.ForeignKey("workouts.id"), nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey("exercises.id"), nullable=False
    )
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    # ── Table Constraints ─────────────────────────────────────────────────────
    __table_args__ = (
        # An exercise can only appear once per workout
        db.UniqueConstraint(
            "workout_id", "exercise_id",
            name="uq_workout_exercise"
        ),
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # ── Model Validations ─────────────────────────────────────────────────────
    @validates("reps")
    def validate_reps(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("Reps must be a positive integer.")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("Sets must be a positive integer.")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        if value is not None and (not isinstance(value, int) or value < 1):
            raise ValueError("Duration must be a positive number of seconds.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id} sets={self.sets} reps={self.reps}>"
        )
