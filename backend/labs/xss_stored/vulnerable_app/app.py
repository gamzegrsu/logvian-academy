from flask import Flask, request, render_template_string

app = Flask(__name__)

comments = []

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        comment = request.form.get("comment")
        comments.append(comment)
    return render_template_string("""
        <h2>Yorum Alanı</h2>
        <form method="POST">
            <input type="text" name="comment" />
            <button type="submit">Gönder</button>
        </form>
        <hr>
        {% for c in comments %}
          <p>{{ c|safe }}</p>
        {% endfor %}
    """, comments=comments)

@app.route("/flag")
def flag():
    return "FLAG{xss_wizard}"