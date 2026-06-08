# --- Import Necessary Libraries ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Scikit-Learn modules for preprocessing, modeling, and evaluation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn import tree

def generate_synthetic_data(n_samples=100):
    """
    Generates a larger sample dataset. Machine learning models need sufficient 
    data to learn patterns effectively. 10 samples are generally too few.
    """
    np.random.seed(42) # Ensures reproducibility
    
    # Generate random study hours (0 to 12) and previous scores (30 to 100)
    study_hours = np.random.uniform(0, 12, n_samples)
    prev_scores = np.random.uniform(30, 100, n_samples)
    
    # Create a logical relationship: passing requires a mix of good previous scores and study time.
    # We add some random noise so the data isn't perfectly predictable.
    combined_score = (study_hours * 5) + (prev_scores * 0.5) + np.random.normal(0, 5, n_samples)
    
    # Pass if the combined metric is above a threshold (e.g., 60)
    passed = (combined_score > 60).astype(int)
    
    return pd.DataFrame({
        'StudyHours': study_hours,
        'PrevExamScore': prev_scores,
        'Pass': passed
    })

def main():
    # --- 1. Data Preparation ---
    df = generate_synthetic_data(100)
    
    print("\n=== Data Overview ===")
    print("First 5 rows of the dataset:")
    print(df.head())

    # Separate our input features (X) from our target variable (y)
    X = df[['StudyHours', 'PrevExamScore']]
    y = df['Pass']

    # Split the dataset. 
    # Why? We train on one subset and test on unseen data to ensure the model 
    # actually learned the underlying pattern, rather than just memorizing the data (overfitting).
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"\nTraining data size: {X_train.shape[0]} samples")
    print(f"Testing data size: {X_test.shape[0]} samples")

    # --- 2. Feature Scaling ---
    # Logistic Regression performs better when features are on a similar scale.
    # StudyHours (0-12) and PrevExamScore (30-100) have very different ranges. 
    # StandardScaler normalizes them to have a mean of 0 and standard deviation of 1.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # IMPORTANT: We only transform (not fit) the test data to prevent "data leakage" 
    # from the test set into the training phase.
    X_test_scaled = scaler.transform(X_test)


    # --- 3. Model Training ---
    
    # Model A: Logistic Regression (Good for linear relationships)
    logreg_model = LogisticRegression()
    logreg_model.fit(X_train_scaled, y_train)
    y_pred_logreg = logreg_model.predict(X_test_scaled)
    accuracy_logreg = accuracy_score(y_test, y_pred_logreg)

    # Model B: Decision Tree (Good for non-linear, step-based logic)
    # We limit max_depth to 3 to prevent the tree from becoming too complex and overfitting the training data.
    tree_model = DecisionTreeClassifier(random_state=42, max_depth=3)
    tree_model.fit(X_train, y_train) # Note: Trees do not require scaled data
    y_pred_tree = tree_model.predict(X_test)
    accuracy_tree = accuracy_score(y_test, y_pred_tree)


    # --- 4. Model Evaluation ---
    # We look beyond just 'accuracy' using the Confusion Matrix and Classification Report 
    # to understand false positives and false negatives.
    print("\n=== Model Evaluation ===")
    
    print("\nLogistic Regression:")
    print(f"Accuracy: {accuracy_logreg:.2f}")
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_logreg))
    print("Classification Report:\n", classification_report(y_test, y_pred_logreg))

    print("\nDecision Tree:")
    print(f"Accuracy: {accuracy_tree:.2f}")
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred_tree))
    print("Classification Report:\n", classification_report(y_test, y_pred_tree))


    # --- 5. Visualization ---
    # Visualizing the Decision Tree helps us understand the exact rules the model created.
    plt.figure(figsize=(14, 8))
    tree.plot_tree(tree_model, 
                   feature_names=['StudyHours', 'PrevExamScore'], 
                   class_names=['Fail', 'Pass'], 
                   filled=True, 
                   rounded=True,
                   fontsize=10)
    plt.title("Decision Tree for Pass/Fail Classification")
    plt.show()


    # --- 6. Interactive Prediction Loop ---
    print("\n=== Interactive Prediction ===")
    print("Enter student data to predict if they will pass or fail.")
    print("Type 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("Enter study hours (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
                
            study_hours = float(user_input)
            prev_exam_score = float(input("Enter previous exam score (0-100): "))
            
            # Input validation to prevent impossible scenarios
            if study_hours < 0 or prev_exam_score < 0 or prev_exam_score > 100:
                print("Error: Study hours must be non-negative, and exam score must be between 0 and 100.")
                continue
            
            # Format the raw input exactly how the models expect it
            new_data = pd.DataFrame([[study_hours, prev_exam_score]], 
                                  columns=['StudyHours', 'PrevExamScore'])
            
            # Remember to scale the input data for the Logistic Regression model!
            new_data_scaled = scaler.transform(new_data)
            
            # Generate Predictions
            logreg_pred = logreg_model.predict(new_data_scaled)[0]
            tree_pred = tree_model.predict(new_data)[0]
            
            # Display Results
            print("\n--- Predictions ---")
            print(f"Logistic Regression predicts: {'Pass' if logreg_pred == 1 else 'Fail'}")
            print(f"Decision Tree predicts:       {'Pass' if tree_pred == 1 else 'Fail'}")
            print("-" * 40 + "\n")
            
        except ValueError:
            print("Error: Please enter valid numerical values.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# Run the script
if __name__ == "__main__":
    main()
