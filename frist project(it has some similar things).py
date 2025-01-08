import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
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
        try:
            speed = input("Enter speed (or 'done' to finish): ")
            if speed.lower() == 'done':
                break
            distance = input("Enter distance (or 'done' to finish): ")
            if distance.lower() == 'done':
                break
            
            speeds.append(float(speed))
            distances.append(float(distance))
        except ValueError:
            print("Invalid input. Please enter numerical values for speed and distance.")

    # Check if there's enough data to proceed
    if len(speeds) == 0 or len(distances) == 0:
        print("No data entered. Exiting.")
        exit()

    data = {'Speed': speeds, 'Distance': distances}
    return pd.DataFrame(data)

# Function to perform cross-validation
def cross_validate_model(model, X, y):
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    return np.mean(cv_scores)

# Function to plot evaluation metrics and data
def plot_results(X_train, y_train, X_test, y_test, y_pred, model):
    # Plot the training and testing data points
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.scatter(X_train, y_train, color='green', label='Training Data')
    plt.scatter(X_test, y_test, color='blue', label='Testing Data')
    plt.plot(X_test, y_pred, color='red', label='Regression Line')
    plt.xlabel('Speed (normalized)')
    plt.ylabel('Distance')
    plt.title('Car Distance vs. Speed')
    plt.legend()

    # Plot residuals
    residuals = y_test - y_pred
    plt.subplot(1, 2, 2)
    plt.scatter(X_test, residuals, color='purple', label='Residuals')
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel('Speed (normalized)')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Function to run the linear regression model
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
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)

    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"R-squared: {r2}")

    # Perform Cross-Validation
    cv_score = cross_validate_model(model, X, y)
    print(f"Cross-Validation (Mean MSE): {cv_score}")

    # Plot the results
    plot_results(X_train, y_train, X_test, y_test, y_pred, model)

# Function to make predictions with the trained model
def predict_new_data(model):
    try:
        speed_input = float(input("Enter the speed to predict distance: "))
        normalized_speed = normalize_data([[speed_input]])  # Normalize the input speed
        predicted_distance = model.predict(normalized_speed)
        print(f"Predicted Distance: {predicted_distance[0]}")
    except ValueError:
        print("Invalid input. Please enter a numeric value.")

# Run the linear regression model
if __name__ == '__main__':
    run_linear_regression()

    # Predict new data after training
    predict_new_data(model)
