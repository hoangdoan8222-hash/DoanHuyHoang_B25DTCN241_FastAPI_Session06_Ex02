from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

students = [
    {"id": 1, "code": "SV001", "name": "Nguyen Van A", "email": "a@gmail.com", "age": 20},
    {"id": 2, "code": "SV002", "name": "Tran Thi B", "email": "b@gmail.com", "age": 22},
    {"id": 3, "code": "SV003", "name": "Le Van C", "email": "c@gmail.com", "age": 18}
]


class Student(BaseModel):
    code: str
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    age: int = Field(..., gt=0)

@app.post("/students")
def create_student(student: Student):
    for s in students:
        if s["code"] == student.code:
            raise HTTPException(status_code=400, detail="Student code already exists")

    new_student = {
        "id": max([s["id"] for s in students]) + 1 if students else 1,
        **student.model_dump()
    }

    students.append(new_student)
    return new_student

@app.get("/students")
def get_students(
    keyword: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
):
    result = students

    if keyword:
        keyword = keyword.lower()
        result = [
            s for s in result
            if keyword in s["name"].lower()
            or keyword in s["code"].lower()
            or keyword in s["email"].lower()
        ]

    if min_age is not None:
        result = [s for s in result if s["age"] >= min_age]

    if max_age is not None:
        result = [s for s in result if s["age"] <= max_age]

    return result

@app.get("/students/{student_id}")
def get_student(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student

    raise HTTPException(status_code=404, detail="Student not found")


@app.put("/students/{student_id}")
def update_student(student_id: int, updated: Student):
    for i, student in enumerate(students):
        if student["id"] == student_id:

            # Kiểm tra code trùng (trừ chính học viên đang sửa)
            for s in students:
                if s["code"] == updated.code and s["id"] != student_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Student code already exists"
                    )

            students[i] = {
                "id": student_id,
                **updated.model_dump()
            }

            return students[i]

    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    for i, student in enumerate(students):
        if student["id"] == student_id:
            return students.pop(i)

    raise HTTPException(status_code=404, detail="Student not found")