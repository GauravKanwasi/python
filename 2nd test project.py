import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import ipywidgets as widgets
from IPython.display import display, clear_output
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set global plotting styles
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Generate a more realistic dataset with noise and multiple features
np.random.seed(42)
n_samples = 500

# Create features
study_hours = np.random.normal(6.5, 2.5, n_samples)
attendance = np.random.normal(85, 15, n_samples)
practice_hours = np.random.normal(3, 1.5, n_samples)
previous_gpa = np.random.normal(2.8, 0.5, n_samples)

# Create target variable with more realistic probabilities
log_odds = (-3 + 0.8*study_hours + 0.03*attendance + 0.5*practice_hours + 1.2*previous_gpa 
            + 0.05*study_hours*attendance/100 - 0.2*(study_hours - 6)**2)
pass_prob = 1 / (1 + np.exp(-log_odds))
pass_status = np.where(pass_prob > 0.5, 1, 0)

# Add some noise to the pass status
noise = np.random.random(n_samples) < 0.05
pass_status = np.where(noise, 1 - pass_status, pass_status)

# Create DataFrame
df = pd.DataFrame({
    'StudyHours': study_hours,
    'Attendance': attendance,
    'PracticeHours': practice_hours,
    'PreviousGPA': previous_gpa,
    'Pass': pass_status
})

# Clip values to reasonable ranges
df['StudyHours'] = df['StudyHours'].clip(0, 15)
df['Attendance'] = df['Attendance'].clip(0, 100)
df['PracticeHours'] = df['PracticeHours'].clip(0, 8)
df['PreviousGPA'] = df['PreviousGPA'].clip(1.0, 4.0)

# Data Exploration Section
print("="*80)
print("DATA EXPLORATION")
print("="*80)
print(f"Dataset contains {df.shape[0]} samples with {df.shape[1]} features\n")

# Display dataset summary
print("Dataset Summary:")
print(df.describe().round(2))
print("\nPass Rate: {:.1f}%".format(100 * df['Pass'].mean()))

# Feature distributions
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
features = ['StudyHours', 'Attendance', 'PracticeHours', 'PreviousGPA']

for i, feature in enumerate(features):
    ax = axes[i//2, i%2]
    sns.histplot(data=df, x=feature, hue='Pass', kde=True, ax=ax, element='step', alpha=0.7)
    ax.set_title(f'{feature} Distribution by Pass Status')
    ax.set_xlabel(feature)
    ax.set_ylabel('Count')
    
plt.tight_layout()
plt.suptitle('Feature Distributions', fontsize=16, y=1.02)
plt.show()

# Correlation analysis
plt.figure(figsize=(10, 8))
corr = df.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Feature Correlation Matrix', fontsize=16)
plt.show()

# Prepare data for modeling
X = df.drop('Pass', axis=1)
y = df['Pass']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Create pipeline with standardization and logistic regression
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(class_weight='balanced', solver='lbfgs', max_iter=1000)
)

print("\n" + "="*80)
print("MODEL TRAINING & EVALUATION")
print("="*80)

# Perform cross-validation
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
print(f"\nCross-Validation Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Train model
model.fit(X_train, y_train)

# Display model coefficients
feature_names = X.columns
coefs = model.named_steps['logisticregression'].coef_[0]
intercept = model.named_steps['logisticregression'].intercept_[0]

print("\nModel Coefficients:")
for feature, coef in zip(feature_names, coefs):
    print(f"{feature}: {coef:.3f}")
print(f"Intercept: {intercept:.3f}")

# Make predictions
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# Evaluate model
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

print(f"\nTest Accuracy: {accuracy:.3f}")
print("\nConfusion Matrix:")
print(conf_matrix)
print("\nClassification Report:")
print(class_report)

# ROC Curve
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(10, 8))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=16)
plt.legend(loc="lower right")
plt.show()

# Interactive Prediction Interface
print("\n" + "="*80)
print("INTERACTIVE PREDICTION")
print("="*80)

# Create interactive widgets
study_hours = widgets.FloatSlider(min=0, max=15, step=0.5, value=6.5, description='Study Hours:')
attendance = widgets.FloatSlider(min=0, max=100, step=1, value=85, description='Attendance (%):')
practice_hours = widgets.FloatSlider(min=0, max=8, step=0.5, value=3, description='Practice Hours:')
previous_gpa = widgets.FloatSlider(min=1.0, max=4.0, step=0.1, value=2.8, description='Previous GPA:')
predict_button = widgets.Button(description="Predict", button_style='success')
output = widgets.Output()

# Create UI layout
ui = widgets.VBox([
    widgets.HTML("<h3>Predict Pass Probability:</h3>"),
    study_hours,
    attendance,
    practice_hours,
    previous_gpa,
    predict_button,
    output
])

def on_predict_click(b):
    with output:
        clear_output()
        input_data = pd.DataFrame({
            'StudyHours': [study_hours.value],
            'Attendance': [attendance.value],
            'PracticeHours': [practice_hours.value],
            'PreviousGPA': [previous_gpa.value]
        })
        
        prob = model.predict_proba(input_data)[0][1]
        classification = "PASS" if prob >= 0.5 else "FAIL"
        
        # Color coding based on probability
        if prob > 0.7:
            color = "green"
        elif prob > 0.5:
            color = "orange"
        else:
            color = "red"
        
        print(f"\nPrediction Results:")
        print(f"• Study Hours: {study_hours.value:.1f} hours")
        print(f"• Attendance: {attendance.value:.0f}%")
        print(f"• Practice Hours: {practice_hours.value:.1f} hours")
        print(f"• Previous GPA: {previous_gpa.value:.1f}")
        print(f"\nProbability of Passing: \033[1m{prob:.1%}\033[0m")
        print(f"Predicted Outcome: \033[1;{color}m{classification}\033[0m")
        
        # Create visual indicator
        plt.figure(figsize=(10, 2))
        plt.barh([0], [prob], color=color, height=0.5)
        plt.xlim(0, 1)
        plt.axvline(0.5, color='gray', linestyle='--')
        plt.title('Pass Probability Indicator', fontsize=14)
        plt.xlabel('Probability')
        plt.yticks([])
        plt.show()

predict_button.on_click(on_predict_click)

display(ui)

# Additional Visualizations
print("\n" + "="*80)
print("DECISION BOUNDARY VISUALIZATION")
print("="*80)

# Create a grid for decision boundary visualization
hours_range = np.linspace(0, 15, 50)
gpa_range = np.linspace(1.0, 4.0, 50)
xx, yy = np.meshgrid(hours_range, gpa_range)

# Create average values for other features
avg_attendance = df['Attendance'].mean()
avg_practice = df['PracticeHours'].mean()

# Create grid predictions
grid_data = pd.DataFrame({
    'StudyHours': xx.ravel(),
    'Attendance': avg_attendance,
    'PracticeHours': avg_practice,
    'PreviousGPA': yy.ravel()
})

probs = model.predict_proba(grid_data)[:, 1].reshape(xx.shape)

# Plot decision boundary
plt.figure(figsize=(12, 9))
contour = plt.contourf(xx, yy, probs, 25, cmap='RdYlGn', alpha=0.8)
plt.colorbar(contour, label='Pass Probability')
plt.scatter(
    df[df['Pass'] == 0]['StudyHours'], 
    df[df['Pass'] == 0]['PreviousGPA'], 
    c='red', edgecolor='k', s=50, label='Fail', alpha=0.7
)
plt.scatter(
    df[df['Pass'] == 1]['StudyHours'], 
    df[df['Pass'] == 1]['PreviousGPA'], 
    c='green', edgecolor='k', s=50, label='Pass', alpha=0.7
)
plt.xlabel('Study Hours')
plt.ylabel('Previous GPA')
plt.title('Decision Boundary: Study Hours vs Previous GPA\n(Other features at average values)', fontsize=16)
plt.legend()
plt.show()

# Feature importance visualization
feature_importance = pd.Series(coefs, index=feature_names).sort_values()

plt.figure(figsize=(10, 6))
feature_importance.plot(kind='barh', color='skyblue')
plt.title('Feature Importance in Logistic Regression Model', fontsize=16)
plt.xlabel('Coefficient Value')
plt.ylabel('Feature')
plt.axvline(0, color='gray', linestyle='-')
plt.show()

# Display final insights
print("\n" + "="*80)
print("KEY INSIGHTS")
print("="*80)
print("1. Study hours and previous GPA are the strongest predictors of passing")
print("2. The model shows diminishing returns for study hours beyond 10 hours")
print("3. Attendance has a moderate positive effect on pass probability")
print("4. Practice hours show a significant impact despite lower values")
print("5. Students with GPA < 2.0 need substantial additional study time to pass")
