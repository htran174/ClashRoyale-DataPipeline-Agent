from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.get("/")
def index():
    # later we'll load stats from SQLite
    sample_stats = {
        "matches": 0,
        "decks": 0,
        "last_updated": "Not loaded yet"
    }
    return render_template("home.html", stats=sample_stats)

if __name__ == "__main__":
    app.run(debug=True)
