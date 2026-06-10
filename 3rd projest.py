import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

# =====================================================
# Sample dataset: Study hours, previous exam scores,
# and pass/fail labels
# =====================================================
data = {
    "StudyHours": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "PrevExamScore": [30, 40, 45, 50, 60, 65, 70, 75, 80, 85],
    "Pass": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]  # 0 = Fail, 1 = Pass
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Display dataset overview
print("\n=== Dataset Overview ===")
print(df)
print(f"\nDataset Size: {df.shape}")

# Features (X) and Target (y)
X = df[["StudyHours", "PrevExamScore"]]
y = df["Pass"]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print(f"\nTraining Data Size: {X_train.shape}")
print(f"Testing Data Size: {X_test.shape}")

# =====================================================
# Train multiple decision tree models
# =====================================================
def train_models(X_train, y_train):
    models = {}

    for depth in range(1, 6):
        model = DecisionTreeClassifier(
            max_depth=depth,
            random_state=42
        )

        model.fit(X_train, y_train)
        models[depth] = model

    return models


# =====================================================
# Evaluate all trained models
# =====================================================
def evaluate_models(models, X_test, y_test):
    best_model = None
    best_depth = None
    best_accuracy = 0

    print("\n=== Model Evaluation ===")

    for depth, model in models.items():
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\nMax Depth: {depth}")
        print(f"Accuracy : {accuracy:.2f}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model
            best_depth = depth

    print(
        f"\nBest Model -> Depth={best_depth}, "
        f"Accuracy={best_accuracy:.2f}"
    )

    return best_model, best_depth


# =====================================================
# Detailed performance report
# =====================================================
def detailed_report(model, X_test, y_test):
    y_pred = model.predict(X_test)

    print("\n=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, zero_division=0))


# =====================================================
# Predict student result
# =====================================================
def predict_student(model):
    try:
        study_hours = float(input("Enter study hours: "))
        prev_exam_score = float(input("Enter previous exam score: "))

        if study_hours < 0 or prev_exam_score < 0:
            print("Values must be non-negative.")
            return

        # Use DataFrame to avoid sklearn warnings
        sample = pd.DataFrame({
            "StudyHours": [study_hours],
            "PrevExamScore": [prev_exam_score]
        })

        prediction = model.predict(sample)[0]

        result = "Pass" if prediction == 1 else "Fail"

        print(f"\nPrediction: {result}")

    except ValueError:
        print("Please enter valid numerical values.")


# =====================================================
# Visualize decision tree
# =====================================================
def visualize_tree(model, depth):
    plt.figure(figsize=(12, 8))

    plot_tree(
        model,
        feature_names=["StudyHours", "PrevExamScore"],
        class_names=["Fail", "Pass"],
        filled=True,
        rounded=True
    )

    plt.title(f"Decision Tree (max_depth={depth})")

    # Save tree image
    plt.savefig(f"decision_tree_depth_{depth}.png")
    plt.show()

    print(
        f"Tree image saved as "
        f"'decision_tree_depth_{depth}.png'"
    )


# =====================================================
# Display feature importance
# =====================================================
def show_feature_importance(model):
    print("\n=== Feature Importance ===")

    features = ["StudyHours", "PrevExamScore"]

    for feature, importance in zip(
        features,
        model.feature_importances_
    ):
        print(f"{feature}: {importance:.4f}")


# =====================================================
# Main program
# =====================================================
def main():

    models = train_models(X_train, y_train)

    best_model, best_depth = evaluate_models(
        models,
        X_test,
        y_test
    )

    detailed_report(best_model, X_test, y_test)

    while True:

        print("\n===== Student Prediction System =====")
        print("1. Predict Student Result")
        print("2. Visualize Best Tree")
        print("3. Show Feature Importance")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            predict_student(best_model)

        elif choice == "2":
            visualize_tree(best_model, best_depth)

        elif choice == "3":
            show_feature_importance(best_model)

        elif choice == "4":
            print("Exiting program...")
            break

        else:
            print("Invalid option. Please try again.")


# Run the program
if __name__ == "__main__":
    main()
