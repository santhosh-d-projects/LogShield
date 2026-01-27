import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

DATA_FILE = "data/features.csv"
MODEL_FILE = "models/root_cause_model.pkl"

# create models folder
import os
os.makedirs("models", exist_ok=True)


print("📥 Loading dataset...")
df = pd.read_csv(DATA_FILE)

X = df.drop(columns=["window_start", "label"])
y = df["label"]

print("Classes:", y.unique())

# encode labels
le = LabelEncoder()
y_enc = le.fit_transform(y)

# train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.25, random_state=42, stratify=y_enc
)

print("🤖 Training RandomForest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

model.fit(X_train, y_train)

# evaluate
y_pred = model.predict(X_test)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# save model + encoder
joblib.dump(model, MODEL_FILE)
joblib.dump(le, "models/label_encoder.pkl")

print("\n✅ Model saved to models/")
