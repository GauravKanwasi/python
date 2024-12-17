import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# Function to normalize the data
def normalize_data(X):
    scaler = StandardScaler()
    return scaler.fit_transform(X)

# Function to get user input for the dataset
def get_user_input():
    speeds = []
    distances = []

    print("Enter your readings. Type 'done' when you are finished.")
    
    while True:
        speed = input("Enter speed: ")
        if speed.lower() == 'done':
            break
        distance = input("Enter distance: ")
        if distance.lower() == 'done':
            break
        
        speeds.append(float(speed))
        distances.append(float(distance))
    
    data = {'Speed': speeds, 'Distance': distances}
    return pd.DataFrame(data)

# Main function to run the linear regression model
def run_linear_regression():
    # Get user input
    df = get_user_input()
    
    # Print the dataset
    print("Dataset:")
    print(df)
    
    # Define features (X) and target (y)
    X = df[['Speed']]
    y = df['Distance']

    # Normalize the data
    X = normalize_data(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Print the shapes of the training and testing sets
    print(f"Training data shape: {X_train.shape}, {y_train.shape}")
    print(f"Testing data shape: {X_test.shape}, {y_test.shape}")

    # Initialize the Linear Regression model
    model = LinearRegression()

    # Train the model on the training data
    model.fit(X_train, y_train)

    # Print the learned parameters (intercept and coefficient)
    print(f"Intercept: {model.intercept_}")
    print(f"Coefficient: {model.coef_[0]}")

    # Make predictions on the testing set
    y_pred = model.predict(X_test)
    print("Predicted Distances:", y_pred)
    print("Actual Distances:", y_test.values)

    # Calculate and print evaluation metrics
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")
    print(f"R-squared: {r2}")

    # Plot the training and testing data points
    plt.scatter(X_train, y_train, color='green', label='Training Data')
    plt.scatter(X_test, y_test, color='blue', label='Testing Data')
    # Plot the regression line
    plt.plot(X_test, y_pred, color='red', label='Regression Line')
    plt.xlabel('Speed (normalized)')
    plt.ylabel('Distance')
    plt.title('Car Distance vs. Speed')
    plt.legend()
    plt.show()

# Run the linear regression model
if __name__ == '__main__':
    run_linear_regression()
