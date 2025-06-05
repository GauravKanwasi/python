import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
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

# Display dataset overview
print("Dataset Overview:")
print(df.head())
print(f"Dataset Size: {df.shape}")

# Features (X) and Target (y)
X = df[['StudyHours', 'PrevExamScore']]
y = df['Pass']

# Split data into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nTraining Data Size: {X_train.shape}, Testing Data Size: {X_test.shape}")

# Train multiple models with different maximum depths
models = {}
for max_depth in range(1, 6):
    model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    model.fit(X_train, y_train)
    models[max_depth] = model

# Evaluate models
print("\nModel Evaluation:")
for max_depth, model in models.items():
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Max Depth {max_depth} - Accuracy: {accuracy:.2f}")

# Function to get user input and predict outcome
def get_user_input_and_predict(models):
    while True:
        max_depth_input = input("\nEnter the maximum depth of the decision tree (1-5, or 'q' to quit): ")
        if max_depth_input.lower() == 'q':
            print("Exiting prediction mode...")
            break
        try:
            max_depth = int(max_depth_input)
            if max_depth not in models:
                print("Invalid maximum depth. Please enter a value between 1 and 5.")
                continue
            selected_model = models[max_depth]
            
            study_hours = input("Enter the number of study hours: ")
            prev_exam_score = input("Enter the previous exam score: ")
            try:
                study_hours = float(study_hours)
                prev_exam_score = float(prev_exam_score)
                if study_hours < 0 or prev_exam_score < 0:
                    print("Inputs must be non-negative numbers.")
                    continue
                prediction = selected_model.predict([[study_hours, prev_exam_score]])
                result = 'Pass' if prediction[0] == 1 else 'Fail'
                print(f"Predicted outcome for {study_hours} study hours and {prev_exam_score} previous exam score (max_depth={max_depth}): {result}")
            except ValueError:
                print("Invalid input. Please enter numerical values for study hours and previous exam score.")
        except ValueError:
            print("Invalid input. Please enter an integer value for the maximum depth.")

# Function to visualize the decision tree
def visualize_tree(models, max_depth):
    if max_depth not in models:
        print("Invalid maximum depth. Please enter a value between 1 and 5.")
        return
    model = models[max_depth]
    plt.figure(figsize=(12, 8))
    tree.plot_tree(model, feature_names=['StudyHours', 'PrevExamScore'], class_names=['Fail', 'Pass'], filled=True)
    plt.title(f'Decision Tree (max_depth={max_depth})')
    plt.show()

# Main interactive loop
def main():
    print("\n=== Student Pass/Fail Prediction System ===")
    while True:
        action = input("Choose an action: [1] Predict, [2] Visualize Tree, [3] Quit: ")
        if action == '1':
            get_user_input_and_predict(models)
        elif action == '2':
            try:
                max_depth = int(input("Enter the maximum depth to visualize (1-5): "))
                visualize_tree(models, max_depth)
            except ValueError:
                print("Please enter a valid integer between 1 and 5.")
        elif action == '3':
            print("Exiting program...")
            break
        else:
            print("Invalid action. Please choose 1, 2, or 3.")

# Run the program
if __name__ == "__main__":
    main()
