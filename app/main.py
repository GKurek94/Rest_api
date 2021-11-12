from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from Rest_api_1.additional import models, schemas, utils
from Rest_api_1.additional.database import engine, get_db



models.Base.metadata.create_all(bind=engine)


app = FastAPI()


while True:
    try:
        connection = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Xodavi321',
                                      cursor_factory=RealDictCursor)
        cursor = connection.cursor()
        print("Database connection was succesful")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]


def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts", response_model=List[ schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

#  SQL CREATE POST STYLE
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_posts(post: Post):
#     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
#                    (post.title, post.content, post.published))
#     new_post = cursor.fetchone()
#     connection.commit()
#     return {"data": new_post}

@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first() #will stop after 1st id equal, with parameter
                                                                    # .all() it will look for every ids in post

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} was not found)')
        # response.status_code = status.HTTP_404_NOT_FOUND ##SAME ANSWER AS WITH RAISE HTTP, BUT UGLY
        # return {"message": f'post with id {id} was not found'}
    return post


# GET 1 POST BY ID BY SQL METHOD
# @app.get("/posts/{id}")
# def get_post(id: int):
#     cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
#     post = cursor.fetchone()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} was not found)')
#         # response.status_code = status.HTTP_404_NOT_FOUND ##SAME ANSWER AS WITH RAISE HTTP, BUT UGLY
#         # return {"message": f'post with id {id} was not found'}
#     return {"post details:": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, )
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int):
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
#    deleted_post = cursor.fetchone()
#    connection.commit()
#
#    if deleted_post is None:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                            detail=f"post {id} does not exist")
#
#    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {id} does not exist")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()


# @app.put("/posts/{id}")
# def update_post(id: int, post: Post):
#    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s""",
#                   (post.title, post.content, post.published, str(id)))
#    updated_post = cursor.fetchone()
#    connection.commit()
#    if updated_post is None:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post {id} does not exist")
#
#    return {"data": updated_post}

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hashing password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
