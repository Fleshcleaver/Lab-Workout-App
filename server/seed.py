#!/usr/bin/env python3
"""
Seed file — resets the database and populates it with sample data.

Run from the server/ directory:
    python seed.py
"""

from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():

    # ── Reset all tables ───────────────────────────────────────────────────────
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    # ── Seed Exercises ─────────────────────────────────────────────────────────
    print("Seeding exercises...")
    e1  = Exercise(name="Barbell Back Squat",  category="strength",    equipment_needed=True)
    e2  = Exercise(name="Bench Press",         category="strength",    equipment_needed=True)
    e3  = Exercise(name="Pull-Up",             category="strength",    equipment_needed=True)
    e4  = Exercise(name="Overhead Press",      category="strength",    equipment_needed=True)
    e5  = Exercise(name="Plank",               category="strength",    equipment_needed=False)
    e6  = Exercise(name="Box Jump",            category="plyometrics", equipment_needed=False)
    e7  = Exercise(name="Kettlebell Swing",    category="strength",    equipment_needed=True)
    e8  = Exercise(name="Treadmill Run",       category="cardio",      equipment_needed=True)
    e9  = Exercise(name="Dumbbell Curl",       category="strength",    equipment_needed=True)
    e10 = Exercise(name="Romanian Deadlift",   category="strength",    equipment_needed=True)

    db.session.add_all([e1, e2, e3, e4, e5, e6, e7, e8, e9, e10])
    db.session.commit()
    print(f"  Added {Exercise.query.count()} exercises.")

    # ── Seed Workouts ──────────────────────────────────────────────────────────
    print("Seeding workouts...")
    w1 = Workout(
        date=date(2024, 6, 3),
        duration_minutes=60,
        notes="Upper body focus — push/pull supersets.",
    )
    w2 = Workout(
        date=date(2024, 6, 5),
        duration_minutes=75,
        notes="Heavy lower body day. Worked up to 85% 1RM squat.",
    )
    w3 = Workout(
        date=date(2024, 6, 7),
        duration_minutes=45,
        notes="Full body conditioning circuit. Kept rest under 60s.",
    )
    w4 = Workout(
        date=date(2024, 6, 8),
        duration_minutes=30,
        notes="Quick cardio and core session.",
    )

    db.session.add_all([w1, w2, w3, w4])
    db.session.commit()
    print(f"  Added {Workout.query.count()} workouts.")

    # ── Seed WorkoutExercises ──────────────────────────────────────────────────
    print("Seeding workout exercises...")

    # Workout 1 — Upper Body
    we1 = WorkoutExercise(workout_id=w1.id, exercise_id=e2.id, sets=4, reps=6)
    we2 = WorkoutExercise(workout_id=w1.id, exercise_id=e3.id, sets=4, reps=8)
    we3 = WorkoutExercise(workout_id=w1.id, exercise_id=e4.id, sets=3, reps=10)
    we4 = WorkoutExercise(workout_id=w1.id, exercise_id=e9.id, sets=3, reps=12)

    # Workout 2 — Lower Body
    we5 = WorkoutExercise(workout_id=w2.id, exercise_id=e1.id, sets=5, reps=5)
    we6 = WorkoutExercise(workout_id=w2.id, exercise_id=e10.id, sets=4, reps=8)
    we7 = WorkoutExercise(workout_id=w2.id, exercise_id=e6.id, sets=4, reps=5)
    we8 = WorkoutExercise(workout_id=w2.id, exercise_id=e5.id, sets=3, duration_seconds=60)

    # Workout 3 — Full Body Conditioning
    we9  = WorkoutExercise(workout_id=w3.id, exercise_id=e7.id, sets=5, reps=20)
    we10 = WorkoutExercise(workout_id=w3.id, exercise_id=e1.id, sets=3, reps=8)
    we11 = WorkoutExercise(workout_id=w3.id, exercise_id=e2.id, sets=3, reps=8)

    # Workout 4 — Cardio & Core
    we12 = WorkoutExercise(workout_id=w4.id, exercise_id=e8.id, duration_seconds=1200)
    we13 = WorkoutExercise(workout_id=w4.id, exercise_id=e5.id, sets=4, duration_seconds=45)

    db.session.add_all([
        we1, we2, we3, we4,
        we5, we6, we7, we8,
        we9, we10, we11,
        we12, we13,
    ])
    db.session.commit()
    print(f"  Added {WorkoutExercise.query.count()} workout-exercise entries.")

    # ── Verify Relationships ───────────────────────────────────────────────────
    print("\nVerifying relationships...")
    sample_workout = Workout.query.first()
    print(f"  Workout: {sample_workout}")
    print(f"  Exercises in this workout: {[e.name for e in sample_workout.exercises]}")

    sample_exercise = Exercise.query.filter_by(name="Barbell Back Squat").first()
    print(f"\n  Exercise: {sample_exercise}")
    print(f"  Appears in {len(sample_exercise.workouts)} workout(s).")

    print("\n✅ Database seeded successfully!")
