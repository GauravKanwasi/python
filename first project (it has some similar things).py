import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# Function to get user input for the dataset
def get_user_input():
    speeds = []
    distances = []

    print("Enter your readings. Type 'done' when you are finished.")
    
    while True:
        speed_input = input("Enter speed (or 'done' to finish): ")
        if speed_input.lower() == 'done':
            break
        distance_input = input("Enter distance (or 'done' to finish): ")
        if distance_input.lower() == 'done':
            break
        
        try:
            speed = float(speed_input)
            distance = float(distance_input)
            speeds.append(speed)
            distances.append(distance)
        except ValueError:
            print("Invalid input. Please enter numerical values for both speed and distance.")

    # Validate the data
    if len(speeds) < 2:
        print("At least two data points are required.")
        exit()
    elif len(set(speeds)) == 1:
        print("All speeds are the same. Cannot perform linear regression.")
        exit()

    data = {'Speed': speeds, 'Distance': distances}
    return pd.DataFrame(data)

# Function to perform cross-validation
def cross_validate_model(pipeline, X, y):
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='neg_mean_squared_error')
    return np.mean(cv_scores)

# Function to plot evaluation metrics and data
def plot_results(X_train, y_train, X_test, y_test, y_pred, pipeline):
    # Extract scaler and model from the pipeline
    scaler = pipeline.named_steps['standardscaler']
    model = pipeline.named_steps['linearregression']
    
    # Get scaler parameters
    mean = scaler.mean_[0]
    std = scaler.scale_[0]
    
    # Get model parameters
    intercept = model.intercept_
    coef = model.coef_[0]
    
    # Convert to original scale
    original_intercept = intercept - coef * mean / std
    original_slope = coef / std
    
    # Plot data and regression line
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.scatter(X_train, y_train, color='green', label='Training Data')
    plt.scatter(X_test, y_test, color='blue', label='Testing Data')
    
    # Regression line in original scale
    x_range = np.linspace(X_test.min(), X_test.max(), 100)
    y_line = original_intercept + original_slope * x_range
    plt.plot(x_range, y_line, color='red', label='Regression Line')
    
    plt.xlabel('Speed')
    plt.ylabel('Distance')
    plt.title('Car Distance vs. Speed')
    plt.legend()

    # Plot residuals
    residuals = y_test - y_pred
    plt.subplot(1, 2, 2)
    plt.scatter(X_test, residuals, color='purple', label='Residuals')
    plt.axhline(y=0, color='black', linestyle='--')
    plt.xlabel('Speed')
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
    
    # Define features and target
    X = df[['Speed']]
    y = df['Distance']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Print shapes
    print(f"Training data shape: {X_train.shape}, {y_train.shape}")
    print(f"Testing data shape: {X_test.shape}, {y_test.shape}")

    # Create and train the pipeline
    pipeline = make_pipeline(StandardScaler(), LinearRegression())
    pipeline.fit(X_train, y_train)

    # Make predictions
    y_pred = pipeline.predict(X_test)
    print("Predicted Distances:", y_pred)
    print("Actual Distances:", y_test.values)

    # Evaluation metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mse)

    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"Root Mean Squared Error (RMSE): {rmse}")
    print(f"R-squared: {r2}")

    # Cross-validation
    cv_score = cross_validate_model(pipeline, X, y)
    print(f"Cross-Validation (Mean MSE): {cv_score}")

    # Plot results
    plot_results(X_train, y_train, X_test, y_test, y_pred, pipeline)

    return pipeline

# Function to make predictions with the trained model
def predict_new_data(pipeline):
    print("Enter speeds to predict distances. Type 'done' when finished.")
    while True:
        speed_input = input("Enter speed (or 'done' to finish): ")
        if speed_input.lower() == 'done':
            break
        try:
            speed = float(speed_input)
            predicted_distance = pipeline.predict([[speed]])
            print(f"Speed: {speed}, Predicted Distance: {predicted_distance[0]}")
        except ValueError:
            print("Invalid input. Please enter a numerical value.")

# Main execution
if __name__ == '__main__':
    pipeline = run_linear_regression()
    predict_new_data(pipeline)
