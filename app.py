from flask import Flask, jsonify, abort
from typing import Tuple
import json
import os

app = Flask(__name__)


def data_loader() -> Tuple[dict, dict]:
    """
    Функция загружает данные из json файлов и преобразует их в dict.
    Функция не должна нарушать изначальную структуру данных.
    """
    base_path = os.path.dirname(__file__)
    posts_path = os.path.join(base_path, 'data', 'posts.json')
    comments_path = os.path.join(base_path, 'data', 'comments.json')

    with open(posts_path, 'r', encoding='utf-8') as posts_file:
        posts_data = json.load(posts_file)
        posts = posts_data.get('posts', [])
    
    with open(comments_path, 'r', encoding='utf-8') as comments_file:
        comments_data = json.load(comments_file)
        comments = comments_data.get('comments', [])
    
    return posts, comments

@app.route("/")
def get_posts():
    """
    На странице / вывести json в котором каждый элемент - это:
    - пост из файла posts.json.
    - для каждой поста указано кол-во комментариев этого поста из файла comments.json

    Формат ответа:
    posts: [
        {
            id: <int>,
            title: <str>,
            body: <str>, 
            author:	<str>,
            created_at: <str>,
            comments_count: <int>
        }
    ],
    total_results: <int>

    Порядок ключей словаря в ответе не важен
    """
    posts, comments = data_loader()

    post_comment_count = {post['id']: 0 for post in posts}
    for comment in comments:
        if comment['post_id'] in post_comment_count:
            post_comment_count[comment['post_id']] += 1

    posts_with_comments = [
        {
            **post,
            "comments_count": post_comment_count[post['id']]
        } for post in posts
    ]

    response = {
        "posts": posts_with_comments,
        "total_results": len(posts_with_comments)
    }
    return jsonify(response)


@app.route("/posts/<int:post_id>")
def get_post(post_id):
    """
    На странице /posts/<post_id> вывести json, который должен содержать:
    - пост с указанным в ссылке id
    - список всех комментариев к новости

    Отдавайте ошибку abort(404), если пост не существует.


    Формат ответа:
    id: <int>,
    title: <str>,
    body: <str>, 
    author:	<str>,
    created_at: <str>
    comments: [
        "user": <str>,
        "post_id": <int>,
        "comment": <str>,
        "created_at": <str>
    ]

    Порядок ключей словаря в ответе не важен
    """
    posts, comments = data_loader()

    post = next((post for post in posts if post['id'] == post_id), None)
    if post is None:
        abort(404, description="Post not found")

    post_comments = [comment for comment in comments if comment['post_id'] == post_id]

    post_detail = {
        **post,
        "comments": post_comments
    }

    return jsonify(post_detail)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
