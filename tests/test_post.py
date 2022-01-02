import pytest
from app import schemas
from app.config import settings
from typing import List

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    def validate(post):
        return schemas.PostOut(**post)
    posts = map(validate, res.json())
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200
    #assert list(posts)[0].Post.id == test_posts[0].id

def test_unauthorize_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")

    assert res.status_code == 401  

def test_unauthorize_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401 

def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/8888888") 

    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())

    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title

@pytest.mark.parametrize("title, content, published", [
    ("create one post", "This is awesome", True),
    ("I love soccor", "Best sport", False),
    ("Politics", "Politics needs a lots of experiences", True)
])
def test_create_post(authorized_client, test_user, title, content, published):
    res = authorized_client.post(f"/posts/", 
                                 json={"title": title, "content": content, "published": published})
    created_post = schemas.PostResponse(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_unauthorize_user_create_posts(client, test_posts):
    res = client.post("/posts/", json={"title": "random", "content": "test"})

    assert res.status_code == 401 

def test_unauthorize_user_delete_posts(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401  

def test_success_delete_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 204  

def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete("/posts/999999")

    assert res.status_code == 404  

def test_delete_other_user_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")

    assert res.status_code == 403 

def test_update_post(authorized_client, test_posts, test_user):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    edited_post = schemas.PostResponse(**res.json())

    assert res.status_code == 200
    assert edited_post.title == data["title"]
    assert edited_post.content == data["content"]

def test_update_other_user_post(authorized_client, test_posts, test_user, test_user_2):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[3].id
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)

    assert res.status_code == 403

def test_unauthorize_user_update_posts(client, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }    
    res = client.put(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401 

def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }        
    res = authorized_client.put("/posts/999999", json=data)

    assert res.status_code == 404  

 
     