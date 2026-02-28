# 🏙️ ProProperty AI — Real Estate Valuation Platform

> **Full-stack ML application** for predicting property prices in real time.
> Built with Python, Streamlit, scikit-learn, SQLAlchemy, and Plotly.

---

## 🔗 Live Demo
[Click here to open the app →](https://your-app.streamlit.app)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Secure Auth | bcrypt-hashed passwords, session management |
| 🤖 ML Valuation | Scikit-learn model with 10+ features wired end-to-end |
| 📊 Analytics Dashboard | Plotly charts: state-wise prices, area vs price, furnishing box plots |
| 📍 Map Explorer | Folium map with colour-coded property markers by price segment |
| 📱 Mobile Responsive | 2-column layouts, collapsed sidebar, fluid charts |
| 🔁 Live GPS | Real-time coordinate capture via browser geolocation |
| 💾 Persistent DB | SQLAlchemy ORM over SQLite (swap-ready for PostgreSQL/Supabase) |
| ±10% Range | Confidence interval displayed alongside every prediction |

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/proproperty-ai.git
cd proproperty-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your trained model files
#    house_model.pkl      — trained sklearn/lightgbm model
#    model_columns.pkl    — list of feature column names

# 4. (Optional) Create .env for secrets
echo "DATABASE_URL=sqlite:///proproperty.db" > .env

# 5. Run
streamlit run proproperty_ai.py
```

---

## 🧠 Model Training (Quick Guide)

```python
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

# 1. Load your dataset
df = pd.read_csv("housing_data.csv")

# 2. Feature engineering
features = ["area", "bedrooms", "bathrooms", "property_age",
            "furnishing", "parking", "has_school", "has_hospital", "has_metro"]
X = df[features]
y = df["price"]

# 3. Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05)
model.fit(X_train, y_train)

# 4. Save
joblib.dump(model, "house_model.pkl")
joblib.dump(list(X.columns), "model_columns.pkl")
```

---

## 🗂️ Project Structure

```
proproperty-ai/
├── proproperty_ai.py      # Main Streamlit app
├── requirements.txt       # Python dependencies
├── house_model.pkl        # Trained ML model (add yours)
├── model_columns.pkl      # Feature column list (add yours)
├── .env                   # Secrets — never commit this!
├── .gitignore
└── README.md
```

---

## ☁️ Deployment

### Streamlit Community Cloud (Free)
1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `proproperty_ai.py` as entry point
4. Add `DATABASE_URL` in Secrets

### Render.com
```
Build command : pip install -r requirements.txt
Start command : streamlit run proproperty_ai.py --server.port $PORT
```

---

## 🔒 Security Notes
- Passwords hashed with **bcrypt** (never stored in plain text)
- Secrets managed via `.env` / environment variables
- `.gitignore` excludes `.env` and the SQLite database

---

## 📄 License
MIT — free to use, modify, and deploy.
