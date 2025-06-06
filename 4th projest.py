# Import libraries
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
from sklearn import tree

# Sample dataset: Study hours, previous exam scores, and pass/fail labels
data = {
    'StudyHours': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'PrevExamScore': [30, 40, 45, 50, 60, 65, 70, 75, 80, 85],
    'Pass': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]  # 0 = Fail, 1 = Pass
}

# Convert to DataFrame
df = pd.DataFrame(data)

# --- Data Exploration ---
print("\n=== Data Overview ===")
print("First 5 rows of the dataset:")
print(df.head())
print("\nDataset Statistics:")
print(df.describe())

# Features (X) and Target (y)
X = df[['StudyHours', 'PrevExamScore']]
y = df['Pass']

# Split data into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"\nTraining data size: {X_train.shape[0]} samples")
print(f"Testing data size: {X_test.shape[0]} samples")

# --- Train Logistic Regression Model ---
logreg_model = LogisticRegression()
logreg_model.fit(X_train, y_train)
y_pred_logreg = logreg_model.predict(X_test)
accuracy_logreg = accuracy_score(y_test, y_pred_logreg)

# --- Train Decision Tree Model ---
tree_model = DecisionTreeClassifier(random_state=42, max_depth=3)  # Limit depth for better visualization
tree_model.fit(X_train, y_train)
y_pred_tree = tree_model.predict(X_test)
accuracy_tree = accuracy_score(y_test, y_pred_tree)

# --- Model Evaluation ---
print("\n=== Model Evaluation ===")
print("\nLogistic Regression:")
print(f"Accuracy: {accuracy_logreg:.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_logreg))
print("Classification Report:")
print(classification_report(y_test, y_pred_logreg))

print("\nDecision Tree:")
print(f"Accuracy: {accuracy_tree:.2f}")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_tree))
print("Classification Report:")
print(classification_report(y_test, y_pred_tree))

# --- Visualize Decision Tree ---
plt.figure(figsize=(12, 8))
tree.plot_tree(tree_model, feature_names=['StudyHours', 'PrevExamScore'], 
               class_names=['Fail', 'Pass'], filled=True, rounded=True)
plt.title("Decision Tree for Pass/Fail Classification")
plt.show()

# --- Interactive Prediction Loop ---
def predict_pass_fail():
    print("\n=== Interactive Prediction ===")
    print("Enter student data to predict if they will pass or fail.")
    print("Type 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("Enter study hours (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
                
            study_hours = float(user_input)
            prev_exam_score = float(input("Enter previous exam score: "))
            
            # Validate input ranges
            if study_hours < 0 or prev_exam_score < 0 or prev_exam_score > 100:
                print("Error: Study hours must be non-negative, and exam score must be between 0 and 100.")
                continue
            
            # Create DataFrame for new data
            new_data = pd.DataFrame([[study_hours, prev_exam_score]], 
                                  columns=['StudyHours', 'PrevExamScore'])
            
            # Predictions
            logreg_pred = logreg_model.predict(new_data)[0]
            tree_pred = tree_model.predict(new_data)[0]
            
            # Display results
            print("\nPredictions:")
            print(f"Logistic Regression: {'Pass' if logreg_pred == 1 else 'Fail'}")
            print(f"Decision Tree: {'Pass' if tree_pred == 1 else 'Fail'}")
            print("-" * 40)
            
        except ValueError:
            print("Error: Please enter valid numerical values.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# --- Model Comparison ---
print("\n=== Model Comparison ===")
print(f"Logistic Regression Accuracy: {accuracy_logreg:.2f}")
print(f"Decision Tree Accuracy: {accuracy_tree:.2f}")
if accuracy_logreg > accuracy_tree:
    print("Logistic Regression performs better on the test data.")
elif accuracy_tree > accuracy_logreg:
    print("Decision Tree performs better on the test data.")
else:
    print("Both models perform equally well on the test data.")

# Run the interactive prediction
predict_pass_fail()
