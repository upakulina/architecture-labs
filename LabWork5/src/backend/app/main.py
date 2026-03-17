import os
import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Gradebook API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GradeCreate(BaseModel):
    student_name: str = Field(min_length=1)
    control_name: str = Field(min_length=1)
    score: float = Field(ge=0, le=10)


def get_conn():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "gradebook_db"),
        user=os.getenv("DB_USER", "gradebook_user"),
        password=os.getenv("DB_PASSWORD", "gradebook_password"),
    )


@app.get("/health")
def health():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    return {"status": "ok"}


@app.get("/api/v1/gradebooks")
def list_gradebooks():
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, course_name, group_name, semester, status
                FROM gradebooks
                ORDER BY id
            """)
            return cur.fetchall()


@app.get("/api/v1/gradebooks/{gradebook_id}")
def get_gradebook(gradebook_id: int):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("""
                SELECT id, course_name, group_name, semester, status
                FROM gradebooks
                WHERE id = %s
            """, (gradebook_id,))
            gradebook = cur.fetchone()

            if not gradebook:
                raise HTTPException(status_code=404, detail="Gradebook not found")

            cur.execute("""
                SELECT id, student_name, control_name, score
                FROM grades
                WHERE gradebook_id = %s
                ORDER BY id
            """, (gradebook_id,))
            grades = cur.fetchall()

    return {
        "gradebook": gradebook,
        "grades": grades
    }


@app.post("/api/v1/gradebooks/{gradebook_id}/grades", status_code=201)
def create_grade(gradebook_id: int, payload: GradeCreate):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id FROM gradebooks WHERE id = %s",
                (gradebook_id,)
            )
            if cur.fetchone() is None:
                raise HTTPException(status_code=404, detail="Gradebook not found")

            cur.execute("""
                INSERT INTO grades (gradebook_id, student_name, control_name, score)
                VALUES (%s, %s, %s, %s)
                RETURNING id, gradebook_id, student_name, control_name, score
            """, (
                gradebook_id,
                payload.student_name,
                payload.control_name,
                payload.score
            ))

            new_grade = cur.fetchone()
            conn.commit()

    return new_grade