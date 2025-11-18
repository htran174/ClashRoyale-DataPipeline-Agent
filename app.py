import os

from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables from .env (for later phases: API key, etc.)
load_dotenv()

app = Flask(__name__)


# -------------------------------------------------------------------
# Routes: UI-only for Phase 1
# -------------------------------------------------------------------

@app.route("/")
def home():
    """
    Overview page.
    """
    return render_template(
        "home.html",
        active_page="home",      # used by navbar to highlight current page
        page_name="home"         # used by <body data-page="..."> for JS routing
    )


@app.route("/cards")
def cards():
    """
    Card analytics page.
    """
    return render_template(
        "cards.html",
        active_page="cards",
        page_name="cards"
    )


@app.route("/archetypes")
def archetypes():
    """
    Deck archetype matchup page.
    """
    return render_template(
        "archetypes.html",
        active_page="archetypes",
        page_name="archetypes"
    )


# Optional simple health check
@app.route("/ping")
def ping():
    return "ok", 200


# -------------------------------------------------------------------
# Entry point (for `python app.py`)
# -------------------------------------------------------------------
if __name__ == "__main__":
    # You can tweak host/port/debug as you like.
    app.run(debug=True)
