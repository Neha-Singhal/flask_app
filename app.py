from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Load blog posts from the JSON file
def load_blog_posts():
    try:
        with open("blog_posts.json", "r") as file:
            posts = json.load(file)
            # Ensure each post has a 'likes' key, initialized to 0 if not present
            for post in posts:
                post.setdefault('likes', 0)
            return posts
    except FileNotFoundError:
        return []

# Save blog posts to the JSON file
def save_blog_posts(posts):
    with open("blog_posts.json", "w") as file:
        json.dump(posts, file, indent=4)


def get_next_id(posts):
    if not posts:
        return  1
    return max(post['id']for post in posts) + 1


# Fetch a blog post by ID
def fetch_post_by_id(post_id):
    blog_posts = load_blog_posts()
    for post in blog_posts:
        if post['id'] == post_id:
            return post
    return None

# Route for the homepage
@app.route('/')
def index():
    blog_posts = load_blog_posts()
    return render_template("index.html", posts=blog_posts)

# Route for adding a new post
@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        author = request.form.get('author').strip()
        title = request.form.get('title').strip()
        content = request.form.get('content').strip()

        # Validate inputs
        if not title or not content:
            return "<h1>Error: Title and Content cannot be empty!</h1>", 400

        blog_posts = load_blog_posts()
        new_post = {
            "id": get_next_id(blog_posts) + 1,  # Assign a new ID
            "author": author,
            "title": title,
            "content": content,
            "likes" : 0
        }
        blog_posts.append(new_post)  # Append the new post to the list
        save_blog_posts(blog_posts)  # Save the updated posts to the JSON file

        return redirect(url_for("index"))  # Redirect back to the homepage

    return render_template("add.html")

# Route for deleting a post
@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    posts = load_blog_posts()
    updated_posts = [post for post in posts if post["id"] != post_id]
    save_blog_posts(updated_posts)
    return redirect(url_for("index"))

# Route for updating a post
@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    posts = load_blog_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if post is None:
        return "<h1>404 - Post Not Found</h1>", 404

    if request.method == "POST":
        post['author'] = request.form['author'].strip()
        post['title'] = request.form['title'].strip()
        post['content'] = request.form['content'].strip()

        if not post['title'] or not post['content']:
            return "<h1>Error: Title and Content cannot be empty!</h1>", 400

        save_blog_posts(posts)
        return redirect(url_for('index'))

    return render_template('update.html', post=post)

# Route for showing a single post
@app.route("/post/<int:post_id>")
def show_post(post_id):
    posts = load_blog_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    if post:
        return render_template('post.html', post=post)  # Render the post details
    return "<h1>404 - Post Not Found</h1>", 404


@app.route('/like/<int:post_id>', methods=["POST"])
def like(post_id):
    posts = load_blog_posts()
    post = next((p for p in posts if p['id'] == post_id), None)

    if post:
        post['likes'] += 1  # Increment the like count
        save_blog_posts(posts)  # Save the updated posts
    return redirect(url_for('index'))  # Redirect to the homepage


if __name__ == '__main__':
    app.run(debug=True, port=5001)