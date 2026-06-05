# ==========================================
# STUDENT PASS PREDICTION SYSTEM
# Enhanced Logistic Regression Project
# ==========================================

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import (
    train_test_split,
    cross_val_score
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    auc
)

from sklearn.calibration import calibration_curve

import joblib

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML

# ==========================================
# SETTINGS
# ==========================================

np.random.seed(42)

plt.style.use("seaborn-v0_8-darkgrid")

sns.set_context("notebook")
sns.set_palette("Set2")

plt.rcParams["figure.figsize"] = (10, 6)

# ==========================================
# DATA GENERATION
# ==========================================

print("=" * 80)
print("GENERATING REALISTIC STUDENT DATASET")
print("=" * 80)

n_samples = 1000

study_hours = np.random.normal(6.5, 2.5, n_samples)
attendance = np.random.normal(85, 12, n_samples)
practice_hours = np.random.normal(3, 1.5, n_samples)
previous_gpa = np.random.normal(2.8, 0.5, n_samples)

study_hours = np.clip(study_hours, 0, 15)
attendance = np.clip(attendance, 0, 100)
practice_hours = np.clip(practice_hours, 0, 8)
previous_gpa = np.clip(previous_gpa, 1.0, 4.0)

# Realistic pass probability formula

log_odds = (
    -5
    + 0.45 * study_hours
    + 0.025 * attendance
    + 0.40 * practice_hours
    + 1.50 * previous_gpa
    + 0.03 * study_hours * attendance / 100
    - 0.08 * ((study_hours - 8) ** 2)
)

pass_prob = 1 / (1 + np.exp(-log_odds))

# Generate target probabilistically

pass_status = np.random.binomial(
    1,
    np.clip(pass_prob, 0, 1)
)

df = pd.DataFrame({
    "StudyHours": study_hours,
    "Attendance": attendance,
    "PracticeHours": practice_hours,
    "PreviousGPA": previous_gpa,
    "Pass": pass_status
})

print(f"\nDataset Shape: {df.shape}")

# ==========================================
# BASIC EDA
# ==========================================

print("\n" + "=" * 80)
print("DATA EXPLORATION")
print("=" * 80)

print(df.head())

print("\nSummary Statistics:\n")
print(df.describe().round(2))

print("\nPass Rate:")
print(f"{100 * df['Pass'].mean():.2f}%")

# ==========================================
# CLASS DISTRIBUTION
# ==========================================

plt.figure(figsize=(7,5))

sns.countplot(
    data=df,
    x="Pass"
)

plt.title("Class Distribution")
plt.xlabel("Pass")
plt.ylabel("Count")

plt.show()

# ==========================================
# FEATURE DISTRIBUTIONS
# ==========================================

features = [
    "StudyHours",
    "Attendance",
    "PracticeHours",
    "PreviousGPA"
]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for i, feature in enumerate(features):

    ax = axes[i // 2, i % 2]

    sns.histplot(
        data=df,
        x=feature,
        hue="Pass",
        kde=True,
        alpha=0.6,
        ax=ax
    )

    ax.set_title(f"{feature} Distribution")

plt.tight_layout()
plt.show()

# ==========================================
# CORRELATION HEATMAP
# ==========================================

plt.figure(figsize=(8,6))

corr = df.corr()

sns.heatmap(
    corr,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("Correlation Matrix")

plt.show()

# ==========================================
# TRAIN TEST SPLIT
# ==========================================

X = df.drop("Pass", axis=1)
y = df["Pass"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# ==========================================
# PIPELINE
# ==========================================

model = Pipeline([
    ("scaler", StandardScaler()),
    (
        "classifier",
        LogisticRegression(
            class_weight="balanced",
            max_iter=2000
        )
    )
])

# ==========================================
# CROSS VALIDATION
# ==========================================

print("\n" + "=" * 80)
print("MODEL TRAINING")
print("=" * 80)

cv_scores = cross_val_score(
    model,
    X_train,
    y_train,
    cv=5,
    scoring="accuracy"
)

print(
    f"Cross Validation Accuracy: "
    f"{cv_scores.mean():.4f} ± {cv_scores.std():.4f}"
)

# ==========================================
# TRAIN MODEL
# ==========================================

model.fit(X_train, y_train)

# ==========================================
# COEFFICIENTS
# ==========================================

classifier = model.named_steps["classifier"]

coefs = classifier.coef_[0]

print("\nStandardized Feature Coefficients:\n")

for feature, coef in zip(X.columns, coefs):
    print(f"{feature:<20}: {coef:.4f}")

# ==========================================
# PREDICTIONS
# ==========================================

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# ==========================================
# METRICS
# ==========================================

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n" + "=" * 80)
print("MODEL EVALUATION")
print("=" * 80)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\nClassification Report\n")
print(classification_report(y_test, y_pred))

# ==========================================
# CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6,5))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Fail", "Pass"],
    yticklabels=["Fail", "Pass"]
)

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

plt.show()

# ==========================================
# ROC CURVE
# ==========================================

fpr, tpr, thresholds = roc_curve(
    y_test,
    y_prob
)

roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8,6))

plt.plot(
    fpr,
    tpr,
    lw=2,
    label=f"AUC = {roc_auc:.3f}"
)

plt.plot([0,1],[0,1],"--")

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")

plt.title("ROC Curve")

plt.legend()

plt.show()

# ==========================================
# PROBABILITY DISTRIBUTION
# ==========================================

plt.figure(figsize=(8,6))

sns.histplot(
    y_prob[y_test == 0],
    color="red",
    label="Actual Fail",
    kde=True
)

sns.histplot(
    y_prob[y_test == 1],
    color="green",
    label="Actual Pass",
    kde=True
)

plt.title("Predicted Probability Distribution")
plt.xlabel("Predicted Probability")
plt.legend()

plt.show()

# ==========================================
# CALIBRATION CURVE
# ==========================================

prob_true, prob_pred = calibration_curve(
    y_test,
    y_prob,
    n_bins=10
)

plt.figure(figsize=(8,6))

plt.plot(
    prob_pred,
    prob_true,
    marker="o"
)

plt.plot(
    [0,1],
    [0,1],
    "--"
)

plt.xlabel("Predicted Probability")
plt.ylabel("Observed Frequency")

plt.title("Calibration Curve")

plt.show()

# ==========================================
# FEATURE IMPORTANCE
# ==========================================

importance = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": coefs,
    "AbsCoefficient": np.abs(coefs)
})

importance = importance.sort_values(
    "AbsCoefficient"
)

plt.figure(figsize=(8,5))

sns.barplot(
    data=importance,
    x="Coefficient",
    y="Feature"
)

plt.title("Feature Importance")

plt.show()

# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "student_pass_predictor.pkl"
)

print("\nModel saved successfully!")

# ==========================================
# INTERACTIVE DASHBOARD
# ==========================================

print("\n" + "=" * 80)
print("INTERACTIVE PREDICTION DASHBOARD")
print("=" * 80)

study_slider = widgets.FloatSlider(
    min=0,
    max=15,
    step=0.5,
    value=6.5,
    description="Study"
)

attendance_slider = widgets.FloatSlider(
    min=0,
    max=100,
    step=1,
    value=85,
    description="Attendance"
)

practice_slider = widgets.FloatSlider(
    min=0,
    max=8,
    step=0.5,
    value=3,
    description="Practice"
)

gpa_slider = widgets.FloatSlider(
    min=1,
    max=4,
    step=0.1,
    value=2.8,
    description="GPA"
)

button = widgets.Button(
    description="Predict",
    button_style="success"
)

output = widgets.Output()

def predict_student(_):

    with output:

        clear_output()

        student = pd.DataFrame({
            "StudyHours":[study_slider.value],
            "Attendance":[attendance_slider.value],
            "PracticeHours":[practice_slider.value],
            "PreviousGPA":[gpa_slider.value]
        })

        prob = model.predict_proba(student)[0,1]

        result = "PASS" if prob >= 0.5 else "FAIL"

        color = (
            "green"
            if prob > 0.7
            else "orange"
            if prob > 0.5
            else "red"
        )

        display(
            HTML(
                f"""
                <h2 style="color:{color}">
                Predicted Outcome: {result}
                </h2>

                <h3>
                Pass Probability: {prob:.1%}
                </h3>
                """
            )
        )

        plt.figure(figsize=(8,1.5))

        plt.barh(
            [0],
            [prob]
        )

        plt.axvline(
            0.5,
            linestyle="--"
        )

        plt.xlim(0,1)

        plt.yticks([])

        plt.title("Pass Probability")

        plt.show()

button.on_click(predict_student)

dashboard = widgets.VBox([
    widgets.HTML("<h2>Student Pass Predictor</h2>"),
    study_slider,
    attendance_slider,
    practice_slider,
    gpa_slider,
    button,
    output
])

display(dashboard)

# ==========================================
# END
# ==========================================

print("\nProject execution completed successfully.")
