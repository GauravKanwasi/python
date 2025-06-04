import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt

# Sample dataset: Study hours and whether students passed or failed
data = {
    'StudyHours': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Pass': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]  # 0 = Fail, 1 = Pass
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the data
print("Dataset Preview:")
print(df.head())

# Features (X) and Target (y)
X = df[['StudyHours']]  # Feature(s)
y = df['Pass']          # Target variable (0 = Fail, 1 = Pass)

# Split data into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Display the shape of the training and testing sets
print(f"\nTraining data: {X_train.shape}, {y_train.shape}")
print(f"Testing data: {X_test.shape}, {y_test.shape}")

# Initialize the Logistic Regression model
model = LogisticRegression()

# Train the model on the training data
model.fit(X_train, y_train)

# Display the model's learned coefficients
print(f"\nIntercept: {model.intercept_[0]:.2f}")
print(f"Coefficient for StudyHours: {model.coef_[0][0]:.2f}")

# Make predictions on the testing set
y_pred = model.predict(X_test)

# Display the predictions
print("\nPredicted Outcomes (Pass/Fail):", y_pred)
print("Actual Outcomes:", y_test.values)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

# Generate confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred)

# Generate classification report
class_report = classification_report(y_test, y_pred)

# Display evaluation metrics
print(f"\nAccuracy: {accuracy:.2f}")
print("Confusion Matrix:")
print(conf_matrix)
print("Classification Report:")
print(class_report)

# Create a range of study hours for plotting
study_hours_range = np.linspace(X['StudyHours'].min(), X['StudyHours'].max(), 100).reshape(-1, 1)

# Calculate predicted probabilities
y_prob = model.predict_proba(study_hours_range)[:, 1]

# Plot all data points and the logistic regression curve
plt.scatter(X_test, y_test, color='blue', label='Test Data')
plt.plot(study_hours_range, y_prob, color='red', label='Logistic Regression Curve')

# Add labels and title
plt.xlabel('Study Hours')
plt.ylabel('Probability of Passing')
plt.title('Logistic Regression: Study Hours vs. Pass/Fail')
plt.legend()

# Show the plot
plt.show()

# Interactive part with enhanced usability
print("\n=== Interactive Prediction ===")
print("Enter study hours to predict the probability of passing and classification.")
print("Use comma-separated values (e.g., 3, 5, 7) or 'q' to quit.")

while True:
    user_input = input("Enter study hours (comma-separated) or 'q' to quit: ")
    if user_input.lower() == 'q':
        print("Exiting... Thank you!")
        break
    try:
        # Parse comma-separated input into a list of floats
        hours_list = [float(h.strip()) for h in user_input.split(',')]
        for hours in hours_list:
            if hours < 0:
                print(f"Invalid input: {hours}. Study hours cannot be negative.")
                continue
            # Predict probability and classify
            prob = model.predict_proba([[hours]])[:, 1][0]
            classification = "Pass" if prob >= 0.5 else "Fail"
            print(f"For {hours} study hours: Probability = {prob:.2f}, Classification = {classification}")
    except ValueError:
        print("Invalid input. Please enter numerical values separated by commas.")
