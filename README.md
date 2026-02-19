# 💪 Workout Tracker API

A RESTful backend API for personal trainers to track workouts and exercises — built with **Flask**, **SQLAlchemy**, **Flask-Migrate**, and **Marshmallow**.

---

## 🗂️ Project Structure

```
workout_api/
├── app/
│   ├── __init__.py           # App factory, extensions (db, migrate)
│   ├── schemas.py            # Marshmallow schemas for all models
│   ├── models/
│   │   ├── __init__.py
│   │   ├── workout.py        # Workout model + validations
│   │   ├── exercise.py       # Exercise model + validations
│   │   └── workout_exercise.py  # Join table model + validations
│   └── routes/
│       ├── __init__.py
│       ├── workout_routes.py          # CRUD for /workouts
│       ├── exercise_routes.py         # CRUD for /exercises
│       └── workout_exercise_routes.py # Nested routes /workouts/<id>/exercises
├── migrations/               # Flask-Migrate generated migrations
├── run.py                    # App entry point
├── seed.py                   # Database seeding script
├── Pipfile
├── .env
└── README.md
```

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repo
git clone git@github.com:Fleshcleaver/Lab-Workout-App.git
cd workout_api

# 2. Install dependencies
pipenv install
pipenv shell

# 3. Initialize the database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 4. Seed the database
python seed.py

# 5. Run the server
flask run
#  → Running on http://127.0.0.1:5555
```

---

## 🗃️ Models & Relationships

### `Workout`
| Column         | Type     | Constraints                        |
|----------------|----------|------------------------------------|
| `id`           | Integer  | Primary Key                        |
| `name`         | String   | Required, max 100 chars            |
| `description`  | String   | Optional, max 500 chars            |
| `trainer_name` | String   | Required, max 100 chars            |
| `date`         | Date     | Required                           |
| `created_at`   | DateTime | Auto-set                           |
| `updated_at`   | DateTime | Auto-updated                       |

### `Exercise`
| Column         | Type    | Constraints                                  |
|----------------|---------|----------------------------------------------|
| `id`           | Integer | Primary Key                                  |
| `name`         | String  | Required, unique, max 100 chars              |
| `muscle_group` | String  | Required, must be a valid group (see below)  |
| `equipment`    | String  | Required, must be valid equipment (see below)|
| `instructions` | Text    | Optional                                     |
| `created_at`   | DateTime| Auto-set                                     |
| `updated_at`   | DateTime| Auto-updated                                 |

**Valid muscle groups:** `chest`, `back`, `shoulders`, `biceps`, `triceps`, `legs`, `glutes`, `core`, `cardio`, `full body`

**Valid equipment:** `barbell`, `dumbbell`, `kettlebell`, `machine`, `cable`, `bodyweight`, `resistance band`, `pull-up bar`, `bench`, `none`

### `WorkoutExercise` *(join table)*
| Column             | Type    | Constraints                         |
|--------------------|---------|-------------------------------------|
| `id`               | Integer | Primary Key                         |
| `workout_id`       | Integer | FK → workouts.id, Required          |
| `exercise_id`      | Integer | FK → exercises.id, Required         |
| `sets`             | Integer | Optional, must be ≥ 1              |
| `reps`             | Integer | Optional, must be ≥ 1              |
| `duration_seconds` | Integer | Optional, must be ≥ 1              |
| `rest_seconds`     | Integer | Default 60, must be ≥ 0            |
| `order`            | Integer | Default 1, must be ≥ 1             |
| `notes`            | String  | Optional, max 300 chars             |

> **Business rule:** Each entry requires either `sets` or `duration_seconds` (or both).
> The combination of `(workout_id, exercise_id, order)` is unique.

**Relationships:**
- `Workout` → many `WorkoutExercise` (cascade delete)
- `Exercise` → many `WorkoutExercise` (cascade delete)

---

## 🔌 API Endpoints

### Workouts

| Method | Endpoint             | Description                                   |
|--------|----------------------|-----------------------------------------------|
| GET    | `/workouts`          | Get all workouts (filter: `?trainer_name=...`)|
| GET    | `/workouts/<id>`     | Get a single workout with its exercises       |
| POST   | `/workouts`          | Create a new workout                          |
| PATCH  | `/workouts/<id>`     | Update a workout                              |
| DELETE | `/workouts/<id>`     | Delete a workout (cascades to exercises)      |

**POST `/workouts` — request body:**
```json
{
  "name": "Morning Blast",
  "description": "Quick full body session",
  "trainer_name": "Jordan Lee",
  "date": "2024-06-10"
}
```

---

### Exercises

| Method | Endpoint              | Description                                            |
|--------|-----------------------|--------------------------------------------------------|
| GET    | `/exercises`          | Get all exercises (filter: `?muscle_group=`, `?equipment=`)|
| GET    | `/exercises/<id>`     | Get a single exercise                                  |
| POST   | `/exercises`          | Create a new exercise                                  |
| PATCH  | `/exercises/<id>`     | Update an exercise                                     |
| DELETE | `/exercises/<id>`     | Delete an exercise                                     |

**POST `/exercises` — request body:**
```json
{
  "name": "Goblet Squat",
  "muscle_group": "legs",
  "equipment": "kettlebell",
  "instructions": "Hold kettlebell at chest, squat deep, drive through heels."
}
```

---

### Workout Exercises (Nested)

| Method | Endpoint                                        | Description                        |
|--------|-------------------------------------------------|------------------------------------|
| GET    | `/workouts/<workout_id>/exercises`              | Get all exercises for a workout    |
| POST   | `/workouts/<workout_id>/exercises`              | Add an exercise to a workout       |
| PATCH  | `/workouts/<workout_id>/exercises/<we_id>`      | Update a workout-exercise entry    |
| DELETE | `/workouts/<workout_id>/exercises/<we_id>`      | Remove an exercise from a workout  |

**POST `/workouts/<id>/exercises` — request body:**
```json
{
  "exercise_id": 3,
  "sets": 4,
  "reps": 8,
  "rest_seconds": 90,
  "order": 1,
  "notes": "Focus on form"
}
```
*Or for timed exercises (e.g., planks):*
```json
{
  "exercise_id": 8,
  "sets": 3,
  "duration_seconds": 60,
  "rest_seconds": 45,
  "order": 2
}
```

---

## ✅ Validation Summary

| Layer         | Mechanism                        | Examples                                         |
|---------------|----------------------------------|--------------------------------------------------|
| SQLAlchemy    | `@db.validates()`                | Non-empty strings, positive integers, max lengths|
| Marshmallow   | Schema field validators          | Length, Range, required fields                   |
| DB Constraint | `UniqueConstraint`               | `(workout_id, exercise_id, order)` unique        |
| DB Constraint | `unique=True` on column          | Exercise names are globally unique               |
| Business logic| Route-level check                | Requires `sets` or `duration_seconds` per entry  |

---

## 🌱 Seed Data

The seed script populates:
- **10 Exercises** across all major muscle groups
- **4 Workouts** with realistic trainer names and dates
- **16 WorkoutExercise entries** with sets/reps or duration

Run it any time to reset to a clean state:
```bash
python seed.py
```

---

## 🧪 Example Requests (curl)

```bash
# Get all workouts
curl http://127.0.0.1:5555/workouts

# Get a single workout (with nested exercises)
curl http://127.0.0.1:5555/workouts/1

# Create a workout
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"name":"Push Day","trainer_name":"Alex","date":"2024-06-15"}'

# Add an exercise to a workout
curl -X POST http://127.0.0.1:5555/workouts/1/exercises \
  -H "Content-Type: application/json" \
  -d '{"exercise_id":2,"sets":4,"reps":6,"rest_seconds":180,"order":1}'

# Filter exercises by muscle group
curl "http://127.0.0.1:5555/exercises?muscle_group=legs"

# Delete a workout
curl -X DELETE http://127.0.0.1:5555/workouts/2
```

---

## 🔢 HTTP Status Codes Used

| Code | Meaning                        |
|------|--------------------------------|
| 200  | Success (GET, PATCH)           |
| 201  | Created (POST)                 |
| 400  | Bad request (no JSON body)     |
| 404  | Resource not found             |
| 409  | Conflict (duplicate entry)     |
| 422  | Unprocessable entity (validation failed) |
