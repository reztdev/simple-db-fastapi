import jwt
import psycopg2
from psycopg2 import sql
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, constr, field_validator
from argon2 import PasswordHasher
from uuid import uuid4
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
ph = PasswordHasher()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


conn = psycopg2.connect(
    host='localhost',
    user='ryzki',
    password='12345',
    database='postgres'
)

class Login(BaseModel):
    email: str
    password: str

class Register(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8) # type: ignore
    role: str

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password length must be at least 8 characters")
        return value


class User(BaseModel):
    id_users: str
    users_name: str
    users_email: str
    users_password: str
    users_role: str


def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, 's3cr3t!@#$%^&*()_+_)(*&^%', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception


@app.get("/users", response_model=list[User])
async def get_all_users():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()

        users = [dict(zip(['id_users', 'users_name', 'users_email', 'users_password', 'users_role'], row)) for row in result]
        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
async def login_for_access_token(form_data: Login):
    email = form_data.email
    password = form_data.password

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE users_email=%s", (email,))
            result = cursor.fetchall()

        if len(result) == 0:
            raise HTTPException(status_code=401, detail="Login failed. User not found")

        valid_password = ph.verify(result[0][3], password)
        if not valid_password:
            raise HTTPException(status_code=401, detail="Login failed. Wrong password")

        # Membuat token JWT menggunakan PyJWT
        token = jwt.encode({
            "id": result[0][0],
            "email": result[0][2],  # (optional)
            "role": result[0][5],
        }, 's3cr3t!@#$%^&*()_+_)(*&^%', algorithm='HS256')

        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/getuser", response_model=dict)
async def get_all_users():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()

        return {
            "status": 200,
            "message": "Get all users",
            "count": f"Total {len(result)} user on database",
            "data": result
        }

    except Exception as e:
        return {
            "status": 500,
            "message": str(e),
            "data": []
        }

# How to run with curl
# curl -X POST "http://localhost:8000/api/register" -H "Content-Type: application/json" -d '{
#   "name": "risena",
#   "email": "adminrisena@risena.com",
#   "password": "adminrisena",
#   "role": "admin" if None -> 'user' (default)
# }'
# ---- If length password < 8 maka use with 'jq'
# curl -X POST "http://localhost:8000/api/register" -H "Content-Type: application/json" -d '{"name": "yusron", "email": "yusron22@risena.com", "password": "yusron", "role": ""}' | jq '.detail[0].msg'

@app.post("/api/register", response_model=dict)
async def register_user(user: Register):
    name = user.name
    email = user.email
    password = user.password
    role = user.role or "user"

    try:
        hashed_password = ph.hash(password)
        user_id = str(uuid4())
        query = sql.SQL("INSERT INTO users (id_users, users_name, users_email, users_password, users_role) VALUES (%s, %s, %s, %s, %s) RETURNING *")
        data = (user_id, name, email, hashed_password, role)
        
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, data)
                result = cursor.fetchone()

            conn.commit()

            return {
                "status": 201,
                "message": "Register success",
                "data": result
            }
        except psycopg2.Error as e:
            raise HTTPException(status_code=400, detail=f"User {email} already exists.")

    except psycopg2.Error as e:
        if e.pgcode == '23505':
            raise HTTPException(status_code=400, detail=f"User {email} already exists.")
        raise HTTPException(status_code=500, detail=str(e))

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/delete/{email}", response_model=dict)
async def delete_user(email: str):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE users_email=%s", (email,))
            result = cursor.rowcount

        if result == 0:
            raise HTTPException(status_code=404, detail=f"User with email {email} not found")

        conn.commit()

        return {
            "status": 200,
            "message": f"Deleted user with email {email} success",
            "data": {}
        }
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


