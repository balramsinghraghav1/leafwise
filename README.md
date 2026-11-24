# Leafwise: Image-Based Plant Disease Detection (Group G176)

Website: landing page, register / login, leaf detection (GoogLeNet trained on PlantVillage), per-user scan history in MongoDB Atlas, disease guide and printable reports.

## 1. Set up (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Put your trained model here
Copy the file you downloaded from Colab to:
```
model/plant_model.pt
```

## 3. Fill in `.env`
Copy `.env.example` to `.env` (if you already have a `.env` with your real values, just keep it).

| Variable | What to paste |
|---|---|
| `MONGODB_URI` | Atlas > Database > Connect > Drivers > connection string (replace `<db_username>` and `<db_password>`) |
| `MONGODB_DB_NAME` | database name, e.g. `leafwise` |
| `FLASK_SECRET_KEY` | a long random string: `python -c "import secrets;print(secrets.token_hex(32))"` (keeps users logged in between restarts) |
| `MODEL_PATH` | leave as `model/plant_model.pt` |

In Atlas, also check **Network Access** allows your IP address.
Collections `users` and `predictions` are created automatically.

## 4. Run
```powershell
python app.py
```
Open http://127.0.0.1:5000. To try it on a phone on the same Wi-Fi, open `http://<your-PC-IP>:5000`.

## Pages
| URL | What |
|---|---|
| `/` | Landing page: project, dataset link, the 14 crops and 26 diseases it detects |
| `/register`, `/login` | Accounts (passwords are hashed, CSRF protected, login attempts rate limited) |
| `/detect` | Upload or take a photo, optional crop selection, top-5 result with advice |
| `/history` | Your past scans, stats, filter, delete |
| `/scan/<id>` | Full printable report of one scan |
| `/guide` | Searchable disease guide (public) |

## Troubleshooting
- **"Model file not found"**: put `plant_model.pt` in `model/` and restart.
- **"database is not reachable"**: check `MONGODB_URI` and Atlas Network Access.
- Everyone logged out after each restart: set a real `FLASK_SECRET_KEY`.
- Retraining: see `train.py` (same format of checkpoint as the Colab notebook).
