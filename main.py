from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List


app = FastAPI()

client = MongoClient("mongodb://localhost:3000/")
db = client["blog"]
posts_collection  = db["posts"]

# Models
class Post(BaseModel):
    title: str
    content: str
    author: str

class Comment(BaseModel):
    text:str
    author: str

class MongoDBPost(Post):
    _id: str

class MongoDBComment(Comment):
    _id: str


# API Routes
@app.post("/posts/", response_model=MongoDBPost)
def create_post(post: Post):
    post_id = posts_collection.insert_one(post.model_dump()).inserted_id
    return {"_id": str(post_id), **post.model_dump()}

@app.get("/posts/", response_model=List[MongoDBPost])
def read_posts():
    return list(posts_collection.find())    

@app.get("/posts/{post_id}", response_model=MongoDBPost)
def read_post(post_id: str):
    post = posts_collection.find_one({"_id": post_id})
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.put("/posts/{post_id}", response_model=MongoDBPost)
def updated_post(post_id: str, post:Post):
    updated_post = posts_collection.find_one_and_update(
        {"_id": post_id}, {"$set": post.model_dump()}, return_document=True
    )
    if updated_post:
        return updated_post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: str):
    result = posts_collection.delete_one({"_id": post_id})
    if result.deleted_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/posts/{post_id}/comments/", response_model=MongoDBComment)
def create_comment(post_id: str, comment: Comment):
    comment_id=posts_collection.find_one({"_id": post_id})
    if comment_id:
        comment_id= posts_collection.update_one({"_id": post_id}, {"$push": {"comments": comment.model_dump()}})
        return {"_id": str(comment_id), **comment.model_dump()}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/posts/{post_id}/like/")
def like_post(post_id: str):
    result = posts_collection.update_one({"_id": post_id}, {"$inc": {"likes": 1}})
    if result.modified_count ==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {"message": "Post liked successfully"}

@app.post("/posts/{post_id}/dislike/")
def dislike_post(post_id: str):
    result = posts_collection.update_one({"_id": post_id}, {"$inc": {"dislike": 1}})
    if result.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return {"message": "Post disliked successfully"}