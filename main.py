import os
import smtplib
from contextlib import asynccontextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import Response
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette import status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import FileResponse

from apps.admin import ProductAdmin, CategoryAdmin, ProductPhotoAdmin
from apps.models import db
from apps.routers import product_router, generate_router
from apps.utils.authentication import AuthBackend
from config import conf


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists('static'):
        os.mkdir('static')
    app.mount("/static", StaticFiles(directory='static'), name='static')
    app.include_router(product_router)
    app.include_router(generate_router)
    await db.create_all()
    yield


app = FastAPI(docs_url=None, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=conf.SECRET_KEY)
admin = Admin(app, db._engine, authentication_backend=AuthBackend(conf.SECRET_KEY))
admin.add_view(ProductAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(ProductPhotoAdmin)


@app.get("/media/{full_path:path}", name='media')
async def get_media(full_path):
    image_path = Path(f'media/{full_path}')
    if not image_path.is_file():
        return Response("Image not found on the server", status.HTTP_404_NOT_FOUND)
    return FileResponse(image_path)


def send_email(email: str, subject: str, body: str):
    sender_email = "shokhruzaibodova@gmail.com"
    password = "waxi023@"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())


# API endpoint
@app.post("/send-email/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    subject = "Notification Subject"
    body = "This is a background notification message."

    background_tasks.add_task(send_email, email, subject, body)

    return {"message": "Notification sent in the background"}