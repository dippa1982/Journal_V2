from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_sqlalchemy import SQLAlchemy
from flask import Response
from flask_migrate import Migrate
from collections import Counter
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import datetime
from calendar import monthcalendar
import os

# --------------------------------------------------
# App Setup
# --------------------------------------------------

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///journal.db'
)
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'local-development-key'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --------------------------------------------------
# Models
# --------------------------------------------------

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )
    
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tags = db.Column(
    db.String(500),
    nullable=True)

    mood_score = db.Column(
        db.Integer,
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

# --------------------------------------------------
# Debug
# --------------------------------------------------

@app.route('/debug-db')
def debug_db():
    return str(db.engine.url)

# --------------------------------------------------
# Flask Login
# --------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    return redirect(url_for('login'))

# --------------------------------------------------
# Register
# --------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect(url_for("register"))

        existing = User.query.filter_by(
            username=username
        ).first()

        if existing:

            flash("That username already exists.")

            return redirect(url_for("register"))

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully.")

        return redirect(url_for("login"))

    return render_template("register.html")


# --------------------------------------------------
# Login
# --------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')

    return render_template('login.html')
# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))

# --------------------------------------------------
# Dashboard
# --------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).all()

    total_entries = len(entries)

    if total_entries:
        average_mood = round(
            sum(entry.mood_score for entry in entries)
            / total_entries,
            1
        )
    else:
        average_mood = 0

    streak = 0

    if entries:

        from datetime import date, timedelta

        unique_days = sorted(
            {
                entry.created_at.date()
                for entry in entries
            },
            reverse=True
        )

        current_day = date.today()

        for day in unique_days:

            if day == current_day:

                streak += 1
                current_day -= timedelta(days=1)

            elif day == current_day:

                streak += 1
                current_day -= timedelta(days=1)

            else:

                break

    return render_template(
        "dashboard.html",
        total_entries=total_entries,
        average_mood=average_mood,
        streak=streak
    )

# --------------------------------------------------
# New Entry
# --------------------------------------------------

@app.route('/new-entry', methods=['GET', 'POST'])
@login_required
def new_entry():

    if request.method == 'POST':

        entry = Entry(
        mood_score=int(request.form['mood_score']),
        content=request.form['content'],
        tags=request.form.get('tags'),
        user_id=current_user.id
        )

        db.session.add(entry)
        db.session.commit()

        flash('Journal entry saved.')

        return redirect(
            url_for('dashboard')
        )

    return render_template(
        'new_entry.html',
        now=datetime.now()
    )

# --------------------------------------------------
# Edit Entry
# --------------------------------------------------

@app.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):

    entry = Entry.query.get_or_404(entry_id)

    if request.method == "POST":

        entry.mood_score = int(request.form["mood_score"])
        entry.tags = request.form["tags"]
        entry.content = request.form["content"]

        db.session.commit()

        flash("Journal entry updated.")

        return redirect(
            url_for(
                "view_entry",
                entry_id=entry.id
            )
        )

    return render_template(
        "edit_entry.html",
        entry=entry
    )

# --------------------------------------------------
# Delete Entry
# --------------------------------------------------

@app.route('/delete-entry/<int:entry_id>')
@login_required
def delete_entry(entry_id):

    entry = Entry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(entry)
    db.session.commit()

    flash('Entry deleted.')

    return redirect(url_for('dashboard'))

# --------------------------------------------------
# Search Entry
# --------------------------------------------------

@app.route("/search")
@login_required
def search():

    query = request.args.get("q", "").strip()

    entries = Entry.query.filter(
        Entry.user_id == current_user.id,
        Entry.content.ilike(f"%{query}%")
    ).order_by(
        Entry.created_at.desc()
    ).all()

    return render_template(
        "search_results.html",
        entries=entries,
        query=query
    )

# --------------------------------------------------
# View Entry
# --------------------------------------------------

@app.route('/entry/<int:entry_id>')
@login_required
def view_entry(entry_id):

    entry = Entry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        'view_entry.html',
        entry=entry
    )

# --------------------------------------------------
# Journal
# --------------------------------------------------
@app.route("/journal")
@login_required
def journal():

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Entry.created_at.desc()
    ).all()

    return render_template(
        "journal.html",
        entries=entries
    )

# --------------------------------------------------
# Calendar
# --------------------------------------------------
@app.route("/calendar")
@login_required
def calendar():

    today = datetime.today()

    year = request.args.get(
        "year",
        default=today.year,
        type=int
    )

    month = request.args.get(
        "month",
        default=today.month,
        type=int
    )

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).all()

    # Store entries by day
    entry_lookup = {}

    for entry in entries:

        if entry.created_at.year == year and entry.created_at.month == month:

            entry_lookup[entry.created_at.day] = entry

    weeks = monthcalendar(year, month)

    return render_template(
        "calendar.html",
        weeks=weeks,
        month=month,
        year=year,
        entry_lookup=entry_lookup
    )

# --------------------------------------------------
# Insights
# --------------------------------------------------

@app.route("/insights")
@login_required
def insights():

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).all()

    # -------------------------
    # Basic Stats
    # -------------------------

    total_entries = len(entries)

    if total_entries:
        average_mood = round(
            sum(entry.mood_score for entry in entries)
            / total_entries,
            1
        )
    else:
        average_mood = 0

    # -------------------------
    # Streak
    # -------------------------

    from datetime import date, timedelta

    streak = 0

    if entries:

        unique_days = sorted(
            {entry.created_at.date() for entry in entries},
            reverse=True
        )

        current_day = date.today()

        for day in unique_days:

            if day == current_day:

                streak += 1
                current_day -= timedelta(days=1)

            else:

                break

    # -------------------------
    # Mood Counts
    # -------------------------

    mood_counts = {
        "happy": 0,
        "calm": 0,
        "anxious": 0,
        "angry": 0,
        "sad": 0,
        "frustrated": 0,
        "grateful": 0,
        "fearful": 0
    }

    for entry in entries:

        if entry.mood_score == 8:
            mood_counts["happy"] += 1

        elif entry.mood_score == 7:
            mood_counts["calm"] += 1

        elif entry.mood_score == 6:
            mood_counts["anxious"] += 1

        elif entry.mood_score == 5:
            mood_counts["angry"] += 1

        elif entry.mood_score == 4:
            mood_counts["sad"] += 1

        elif entry.mood_score == 3:
            mood_counts["frustrated"] += 1

        elif entry.mood_score == 2:
            mood_counts["grateful"] += 1

        elif entry.mood_score == 1:
            mood_counts["fearful"] += 1

    # -------------------------
    # Tags (placeholder)
    # -------------------------

    total_tags = 0
    top_tags = []

    # -------------------------
    # Render Page
    # -------------------------

    return render_template(
        "insights.html",
        entries=entries,
        total_entries=total_entries,
        average_mood=average_mood,
        streak=streak,
        mood_counts=mood_counts,
        top_tags=top_tags,
        total_tags=total_tags
    )

# --------------------------------------------------
# Settings
# --------------------------------------------------

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    if request.method == "POST":

        current_password = request.form.get("current_password")

        new_password = request.form.get("new_password")

        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(
            current_user.password_hash,
            current_password
        ):

            flash("Current password is incorrect.")

            return redirect(url_for("settings"))

        if new_password != confirm_password:

            flash("New passwords do not match.")

            return redirect(url_for("settings"))

        current_user.password_hash = generate_password_hash(
            new_password
        )

        db.session.commit()

        flash("Password updated successfully.")

        return redirect(url_for("settings"))

    return render_template("settings.html")

# --------------------------------------------------
# Export to AI
# --------------------------------------------------

@app.route('/export-markdown')
@login_required
def export_markdown():

    entries = Entry.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Entry.created_at.asc()
    ).all()

    markdown = """
# Journal Metadata

Export Date: 16 June 2026 12:48
Entries Included: 2
Date Range: 16 June 2026 - 16 June 2026

---

# AI Reflection Request

Please analyse these journal entries.

Focus specifically on:

- Relationship patterns
- Assumptions versus evidence
- Evidence collected for emotions
- Emotional regulation
- Progress over time
- Situations where I may be catastrophising or mind-reading
- Situations where my concerns appear well-founded

Do not simply validate my perspective.
Look for alternative interpretations and missing information.
Identify both strengths and blind spots.

Then provide:

1. Key patterns
2. Progress made
3. Current challenges
4. Suggested focus for the next week
5. Suggested focus for the next month
6. Include key point that i should be taking with therapy about 

---

"""


    for entry in entries:

        mood_text = {
    8: "😊 Happy",
    7: "😌 Calm",
    6: "😟 Anxious",
    5: "😠 Angry",
    4: "😔 Sad",
    3: "😤 Frustrated",
    2: "❤️ Grateful",
    1: "😨 Fearful"
}.get(entry.mood_score, "Unknown")

        markdown += f"""## {entry.created_at.strftime('%A %d %B %Y %H:%M')}

Mood: {mood_text}

{entry.content}

---

"""
        filename = datetime.now().strftime(
    "journal_%Y-%m-%d_%H-%M.md")

    return Response(
        markdown,
        mimetype="text/markdown",
        headers={
        "Content-Disposition":
        f"attachment; filename={filename}"
        }
    )

# --------------------------------------------------
# Create Database
# --------------------------------------------------

with app.app_context():
    db.create_all()
    from sqlalchemy import text

with app.app_context():

    try:

        db.session.execute(text("""
            ALTER TABLE entry
            ADD COLUMN tags VARCHAR(255);
            ADD COLUMN username VARCHAR(255);
        """))

        db.session.commit()

        print("Tags column added.")

    except Exception:

        db.session.rollback()

        print("Tags column already exists.")

# --------------------------------------------------
# Run App
# --------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)