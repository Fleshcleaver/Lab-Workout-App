from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


# ── Exercise Schema ────────────────────────────────────────────────────────────
class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="Name must be between 1 and 100 characters.")
    )
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(load_default=False)

    # Nested: workouts that use this exercise (dump only, avoids circular nesting)
    workouts = fields.List(fields.Nested(lambda: WorkoutBriefSchema()), dump_only=True)

    @validates("category")
    def validate_category(self, value):
        valid_categories = [
            "strength", "cardio", "flexibility",
            "balance", "plyometrics", "sports", "other"
        ]
        if value.lower().strip() not in valid_categories:
            raise ValidationError(
                f"Category must be one of: {', '.join(valid_categories)}."
            )

    @validates("name")
    def validate_name(self, value):
        if not value or not value.strip():
            raise ValidationError("Name cannot be empty.")

    @pre_load
    def normalize_strings(self, data, **kwargs):
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        if "category" in data and isinstance(data["category"], str):
            data["category"] = data["category"].strip().lower()
        return data


# ── WorkoutExercise Schema ─────────────────────────────────────────────────────
class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1, error="Reps must be at least 1."))
    sets = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1, error="Sets must be at least 1."))
    duration_seconds = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1, error="Duration must be at least 1 second."))

    # Nested exercise info for display
    exercise = fields.Nested(lambda: ExerciseBriefSchema(), dump_only=True)


# ── Brief/Nested Schemas (avoid circular references) ──────────────────────────
class ExerciseBriefSchema(Schema):
    """Lightweight exercise schema used when nested inside workout responses."""
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    category = fields.Str(dump_only=True)
    equipment_needed = fields.Bool(dump_only=True)


class WorkoutBriefSchema(Schema):
    """Lightweight workout schema used when nested inside exercise responses."""
    id = fields.Int(dump_only=True)
    date = fields.Date(dump_only=True)
    duration_minutes = fields.Int(dump_only=True)
    notes = fields.Str(dump_only=True)


# ── Workout Schema ─────────────────────────────────────────────────────────────
class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=480, error="Duration must be between 1 and 480 minutes.")
    )
    notes = fields.Str(allow_none=True, load_default=None)

    # Nested: exercises with reps/sets/duration details
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)

    @validates("date")
    def validate_date(self, value):
        if value is None:
            raise ValidationError("Date is required.")


# ── Instantiated Schemas ───────────────────────────────────────────────────────
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)
