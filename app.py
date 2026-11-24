import base64
import io
import logging
import os
import re
import secrets
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from functools import wraps

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import (Flask, abort, flash, jsonify, redirect, render_template, request,
                   session, url_for)
from PIL import Image, ImageOps, UnidentifiedImageError
from pymongo import DESCENDING, MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

import knowledge
from predictor import Predictor

load_dotenv()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("leafwise")

app = Flask(__name__)
_secret = os.getenv("FLASK_SECRET_KEY", "").strip()
if not _secret or _secret.startswith("PASTE_"):
    _secret = secrets.token_hex(32)
    log.warning("FLASK_SECRET_KEY is not set in .env: using a temporary key. "
                "Everyone will be logged out whenever the server restarts.")
app.config.update(SECRET_KEY=_secret, MAX_CONTENT_LENGTH=8 * 1024 * 1024,
                  SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  PERMANENT_SESSION_LIFETIME=timedelta(days=7))
ALLOWED = {"png", "jpg", "jpeg", "webp", "bmp"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

predictor = Predictor(os.getenv("MODEL_PATH", "model/plant_model.pt"))

# ------------------------------------------------------------------ database
_client = None
_indexed = False


def mongo_configured() -> bool:
    uri = os.getenv("MONGODB_URI", "").strip()
    return bool(uri) and "<db_password>" not in uri and "<cluster-name>" not in uri


def get_db():
    """Return the MongoDB database, or None when Atlas is not configured / unreachable."""
    global _client, _indexed
    if not mongo_configured():
        return None
    try:
        if _client is None:
            _client = MongoClient(os.getenv("MONGODB_URI").strip(), serverSelectionTimeoutMS=5000)
        db = _client[os.getenv("MONGODB_DB_NAME", "leafwise").strip() or "leafwise"]
        if not _indexed:
            db.users.create_index("email", unique=True)
            db.predictions.create_index([("user_id", 1), ("created_at", -1)])
            _indexed = True
        return db
    except PyMongoError as e:
        log.warning("MongoDB problem: %s", e)
        return None


DB_DOWN = ("The database is not reachable right now. Check MONGODB_URI in .env and that your "
           "IP address is allowed in MongoDB Atlas (Network Access).")

# ------------------------------------------------------------ security helpers
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def csrf_protect():
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token") or ""
        real = session.get("_csrf", "")
        if not real or not secrets.compare_digest(sent.encode(), real.encode()):
            if request.path.startswith("/api/"):
                return jsonify(error="Your session expired. Refresh the page and try again."), 400
            flash("Your session expired. Please try again.", "error")
            return redirect(url_for("index"))


@app.after_request
def headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["Referrer-Policy"] = "same-origin"
    return resp


_fails = defaultdict(list)


def throttled(key):
    now = time.time()
    _fails[key] = [t for t in _fails[key] if now - t < 600]
    return len(_fails[key]) >= 6


def safe_next(n):
    if n and n.startswith("/") and not n.startswith("//") and "\\" not in n:
        return n
    return url_for("detect")


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("uid"):
            if request.path.startswith("/api/"):
                return jsonify(error="Please log in to continue."), 401
            flash("Please log in to continue.", "info")
            return redirect(url_for("login", next=request.full_path.rstrip("?")))
        return f(*a, **kw)
    return wrapper


@app.context_processor
def inject():
    user = {"id": session["uid"], "name": session.get("uname", "")} if session.get("uid") else None
    return {"user": user, "endpoint": request.endpoint,
            "stats": {"crops": knowledge.N_CROPS, "diseases": knowledge.N_DISEASES, "classes": knowledge.N_CLASSES}}


def oid(value):
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


# -------------------------------------------------------------------- images
def to_b64(img, size=480):
    t = img.copy()
    t.thumbnail((size, size))
    buf = io.BytesIO()
    t.save(buf, "JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def scan_view(d):
    return {"id": str(d["_id"]), "crop": d.get("crop", ""), "disease": d.get("disease", ""),
            "healthy": bool(d.get("healthy")), "label": d.get("label", ""),
            "confidence": float(d.get("confidence", 0)), "image": d.get("image", ""),
            "created_at": d["created_at"].isoformat() + "Z", "top": d.get("top", []),
            "crop_given": d.get("crop_given")}


# -------------------------------------------------------------------- pages
@app.get("/")
def index():
    return render_template("index.html", crops=knowledge.CROPS)


@app.get("/guide")
def guide():
    return render_template("guide.html", crops=knowledge.CROPS)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("uid"):
        return redirect(url_for("detect"))
    form = {"name": "", "email": ""}
    error = None
    if request.method == "POST":
        name = " ".join(request.form.get("name", "").split())
        email = request.form.get("email", "").strip().lower()
        pw, pw2 = request.form.get("password", ""), request.form.get("confirm", "")
        form = {"name": name, "email": email}
        if not 2 <= len(name) <= 60:
            error = "Please enter your name (2 to 60 characters)."
        elif not EMAIL_RE.match(email) or len(email) > 120:
            error = "That email address doesn’t look right."
        elif not 8 <= len(pw) <= 128:
            error = "Choose a password with at least 8 characters."
        elif pw != pw2:
            error = "The two passwords don’t match."
        else:
            db = get_db()
            if db is None:
                error = DB_DOWN
            else:
                try:
                    res = db.users.insert_one({"name": name, "email": email,
                                               "pw_hash": generate_password_hash(pw),
                                               "created_at": datetime.now(timezone.utc)})
                    session.clear()
                    session.permanent = True
                    session["uid"], session["uname"] = str(res.inserted_id), name
                    flash(f"Welcome, {name.split()[0]}! Your account is ready.", "ok")
                    return redirect(url_for("detect"))
                except DuplicateKeyError:
                    error = "An account with this email already exists. Try logging in."
                except PyMongoError as e:
                    log.warning("register failed: %s", e)
                    error = DB_DOWN
    return render_template("register.html", form=form, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("uid"):
        return redirect(url_for("detect"))
    nxt = request.values.get("next", "")
    email, error = "", None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("password", "")
        key = f"{request.remote_addr}|{email}"
        if throttled(key):
            error = "Too many failed attempts. Please wait a few minutes and try again."
        else:
            db = get_db()
            if db is None:
                error = DB_DOWN
            else:
                try:
                    u = db.users.find_one({"email": email})
                except PyMongoError as e:
                    log.warning("login failed: %s", e)
                    u, error = None, DB_DOWN
                if error is None:
                    if u and check_password_hash(u["pw_hash"], pw):
                        _fails.pop(key, None)
                        session.clear()
                        session.permanent = True
                        session["uid"], session["uname"] = str(u["_id"]), u.get("name", "")
                        return redirect(safe_next(nxt))
                    _fails[key].append(time.time())
                    error = "Wrong email or password."
    return render_template("login.html", email=email, error=error, next=nxt)


@app.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.get("/detect")
@login_required
def detect():
    return render_template("detect.html", model_ready=predictor.model is not None,
                           model_error=predictor.error, crops=predictor.crops() if predictor.model else [])


@app.post("/api/predict")
@login_required
def api_predict():
    if predictor.model is None:
        return jsonify(error=predictor.error), 503
    f = request.files.get("image")
    if f is None or not f.filename:
        return jsonify(error="Choose a leaf photo first."), 400
    if f.filename.rsplit(".", 1)[-1].lower() not in ALLOWED:
        return jsonify(error="Unsupported file type. Please use a JPG, PNG, WEBP or BMP image."), 400
    try:
        img = ImageOps.exif_transpose(Image.open(f.stream)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return jsonify(error="That file could not be read as an image."), 400
    crop = (request.form.get("crop") or "").strip() or None
    try:
        result = predictor.predict(img, crop)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        log.exception("prediction failed")
        return jsonify(error=f"Prediction failed: {e}"), 500

    top1 = result["top"][0]
    scan_id, note = None, None
    db = get_db()
    if db is None:
        note = "This scan could not be saved to your history (database unreachable)."
    else:
        try:
            r = db.predictions.insert_one({
                "user_id": ObjectId(session["uid"]), "created_at": datetime.now(timezone.utc),
                "crop_given": crop, "top": result["top"], "label": top1["label"], "crop": top1["crop"],
                "disease": top1["disease"], "healthy": top1["healthy"], "confidence": top1["confidence"],
                "image": to_b64(img), "filename": os.path.basename(f.filename)[:120]})
            scan_id = str(r.inserted_id)
        except PyMongoError as e:
            log.warning("could not save scan: %s", e)
            note = "This scan could not be saved to your history."
    return jsonify(result=result, advice=knowledge.advice_for(top1["label"]), note=note,
                   scan_url=url_for("scan", scan_id=scan_id) if scan_id else None)


@app.get("/history")
@login_required
def history():
    db = get_db()
    if db is None:
        return render_template("history.html", scans=[], summary=None, error=DB_DOWN)
    uid = ObjectId(session["uid"])
    try:
        scans = [scan_view(d) for d in db.predictions.find({"user_id": uid}).sort("created_at", DESCENDING).limit(60)]
        total = db.predictions.count_documents({"user_id": uid})
        healthy = db.predictions.count_documents({"user_id": uid, "healthy": True})
        top = list(db.predictions.aggregate([
            {"$match": {"user_id": uid, "healthy": False}},
            {"$group": {"_id": "$label", "n": {"$sum": 1}}}, {"$sort": {"n": -1}}, {"$limit": 1}]))
        common = None
        if top:
            d = knowledge.display(top[0]["_id"])
            common = f'{d["crop"]} – {d["disease"]}'
    except PyMongoError as e:
        log.warning("history failed: %s", e)
        return render_template("history.html", scans=[], summary=None, error=DB_DOWN)
    return render_template("history.html", scans=scans, error=None,
                           summary={"total": total, "healthy": healthy, "diseased": total - healthy, "common": common})


@app.get("/scan/<scan_id>")
@login_required
def scan(scan_id):
    _id = oid(scan_id)
    db = get_db()
    if _id is None:
        abort(404)
    if db is None:
        flash(DB_DOWN, "error")
        return redirect(url_for("history"))
    try:
        d = db.predictions.find_one({"_id": _id, "user_id": ObjectId(session["uid"])})
    except PyMongoError:
        flash(DB_DOWN, "error")
        return redirect(url_for("history"))
    if not d:
        abort(404)
    s = scan_view(d)
    return render_template("scan.html", s=s, advice=knowledge.advice_for(s["label"]))


@app.post("/history/<scan_id>/delete")
@login_required
def delete_scan(scan_id):
    _id, db = oid(scan_id), get_db()
    if _id is None:
        abort(404)
    if db is None:
        flash(DB_DOWN, "error")
    else:
        try:
            db.predictions.delete_one({"_id": _id, "user_id": ObjectId(session["uid"])})
            flash("Scan deleted.", "info")
        except PyMongoError:
            flash(DB_DOWN, "error")
    return redirect(url_for("history"))


@app.post("/history/clear")
@login_required
def clear_history():
    db = get_db()
    if db is None:
        flash(DB_DOWN, "error")
    else:
        try:
            n = db.predictions.delete_many({"user_id": ObjectId(session["uid"])}).deleted_count
            flash(f"Deleted {n} scan{'s' if n != 1 else ''}.", "info")
        except PyMongoError:
            flash(DB_DOWN, "error")
    return redirect(url_for("history"))


@app.errorhandler(404)
def not_found(_):
    if request.path.startswith("/api/"):
        return jsonify(error="Not found."), 404
    return render_template("error.html", code=404, msg="We couldn’t find that page."), 404


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="That image is larger than 8 MB. Please use a smaller photo."), 413


@app.errorhandler(500)
def server_error(_):
    if request.path.startswith("/api/"):
        return jsonify(error="Something went wrong on the server."), 500
    return render_template("error.html", code=500, msg="Something went wrong on our side."), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
