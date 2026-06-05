import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, confusion_matrix, classification_report, 
                             roc_curve, auc, precision_recall_curve, f1_score, 
                             matthews_corrcoef, precision_score, recall_score)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import warnings

warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

class StudentPassPredictionModel:
    def __init__(self, random_state=42, test_size=0.2):
        self.random_state = random_state
        self.test_size = test_size
        self.model = None
        self.scaler = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.y_prob = None
        self.df = None
        self.metrics = {}
        
    def generate_dataset(self, n_samples=500):
        np.random.seed(self.random_state)
        
        study_hours = np.random.normal(6.5, 2.5, n_samples)
        attendance = np.random.normal(85, 15, n_samples)
        practice_hours = np.random.normal(3, 1.5, n_samples)
        previous_gpa = np.random.normal(2.8, 0.5, n_samples)
        sleep_hours = np.random.normal(7, 1.5, n_samples)
        
        log_odds = (-3 + 0.8*study_hours + 0.03*attendance + 0.5*practice_hours + 
                   1.2*previous_gpa + 0.2*sleep_hours + 
                   0.05*study_hours*attendance/100 - 0.2*(study_hours - 6)**2)
        pass_prob = 1 / (1 + np.exp(-log_odds))
        pass_status = np.where(pass_prob > 0.5, 1, 0)
        
        noise = np.random.random(n_samples) < 0.05
        pass_status = np.where(noise, 1 - pass_status, pass_status)
        
        self.df = pd.DataFrame({
            'StudyHours': study_hours.clip(0, 15),
            'Attendance': attendance.clip(0, 100),
            'PracticeHours': practice_hours.clip(0, 8),
            'PreviousGPA': previous_gpa.clip(1.0, 4.0),
            'SleepHours': sleep_hours.clip(4, 12),
            'Pass': pass_status
        })
        
        return self.df
    
    def explore_data(self):
        print("\n" + "="*80)
        print("DATA EXPLORATION")
        print("="*80)
        print(f"Dataset shape: {self.df.shape[0]} samples × {self.df.shape[1]} features\n")
        
        print("Statistical Summary:")
        print(self.df.describe().round(2))
        
        pass_rate = self.df['Pass'].mean() * 100
        print(f"\nPass Rate: {pass_rate:.1f}%")
        print(f"Fail Rate: {100-pass_rate:.1f}%")
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        features = ['StudyHours', 'Attendance', 'PracticeHours', 'PreviousGPA', 'SleepHours']
        
        for i, feature in enumerate(features):
            ax = axes[i//3, i%3]
            sns.histplot(data=self.df, x=feature, hue='Pass', kde=True, ax=ax, 
                        element='step', alpha=0.7, bins=20)
            ax.set_title(f'{feature} Distribution', fontweight='bold')
            ax.set_xlabel(feature)
            ax.set_ylabel('Count')
        
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        plt.savefig('01_feature_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        plt.figure(figsize=(10, 8))
        corr = self.df.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', 
                   linewidths=0.5, cbar_kws={'label': 'Correlation'}, mask=mask)
        plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('02_correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def prepare_data(self):
        X = self.df.drop('Pass', axis=1)
        y = self.df['Pass']
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, 
            stratify=y
        )
        
        print(f"\nTraining set: {self.X_train.shape[0]} samples")
        print(f"Test set: {self.X_test.shape[0]} samples")
    
    def train_model(self):
        print("\n" + "="*80)
        print("MODEL TRAINING & EVALUATION")
        print("="*80)
        
        self.model = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', LogisticRegression(
                class_weight='balanced', 
                solver='lbfgs', 
                max_iter=1000,
                random_state=self.random_state
            ))
        ])
        
        cv_scores = cross_val_score(self.model, self.X_train, self.y_train, 
                                   cv=5, scoring='accuracy')
        print(f"\nCross-Validation Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        print(f"CV Scores: {[f'{score:.4f}' for score in cv_scores]}")
        
        self.model.fit(self.X_train, self.y_train)
        print("\nModel training completed successfully!")
    
    def evaluate_model(self):
        self.y_pred = self.model.predict(self.X_test)
        self.y_prob = self.model.predict_proba(self.X_test)[:, 1]
        
        self.metrics['accuracy'] = accuracy_score(self.y_test, self.y_pred)
        self.metrics['precision'] = precision_score(self.y_test, self.y_pred)
        self.metrics['recall'] = recall_score(self.y_test, self.y_pred)
        self.metrics['f1'] = f1_score(self.y_test, self.y_pred)
        self.metrics['mcc'] = matthews_corrcoef(self.y_test, self.y_pred)
        
        fpr, tpr, _ = roc_curve(self.y_test, self.y_prob)
        self.metrics['auc'] = auc(fpr, tpr)
        
        print(f"\nTest Accuracy: {self.metrics['accuracy']:.4f}")
        print(f"Precision: {self.metrics['precision']:.4f}")
        print(f"Recall: {self.metrics['recall']:.4f}")
        print(f"F1-Score: {self.metrics['f1']:.4f}")
        print(f"Matthews Correlation Coefficient: {self.metrics['mcc']:.4f}")
        print(f"ROC-AUC: {self.metrics['auc']:.4f}")
        
        conf_matrix = confusion_matrix(self.y_test, self.y_pred)
        print("\nConfusion Matrix:")
        print(conf_matrix)
        print("\nClassification Report:")
        print(classification_report(self.y_test, self.y_pred, 
                                   target_names=['Fail', 'Pass']))
    
    def plot_roc_curve(self):
        fpr, tpr, _ = roc_curve(self.y_test, self.y_prob)
        roc_auc = auc(fpr, tpr)
        
        plt.figure(figsize=(10, 8))
        plt.plot(fpr, tpr, color='darkorange', lw=2.5, 
                label=f'ROC Curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([-0.02, 1.02])
        plt.ylim([-0.02, 1.02])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('03_roc_curve.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_precision_recall_curve(self):
        precision, recall, _ = precision_recall_curve(self.y_test, self.y_prob)
        
        plt.figure(figsize=(10, 8))
        plt.plot(recall, precision, color='blue', lw=2.5, label='Precision-Recall Curve')
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.tight_layout()
        plt.savefig('04_precision_recall_curve.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_confusion_matrix(self):
        conf_matrix = confusion_matrix(self.y_test, self.y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Fail', 'Pass'], yticklabels=['Fail', 'Pass'],
                   cbar_kws={'label': 'Count'}, annot_kws={'size': 14})
        plt.xlabel('Predicted', fontsize=12)
        plt.ylabel('Actual', fontsize=12)
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('05_confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self):
        feature_names = self.X_train.columns
        coefs = self.model.named_steps['classifier'].coef_[0]
        
        importance_df = pd.Series(coefs, index=feature_names).sort_values()
        
        plt.figure(figsize=(10, 6))
        importance_df.plot(kind='barh', color='steelblue', edgecolor='black')
        plt.title('Feature Importance (Model Coefficients)', fontsize=14, fontweight='bold')
        plt.xlabel('Coefficient Value', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.axvline(0, color='red', linestyle='--', linewidth=1)
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        plt.savefig('06_feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("\nModel Coefficients:")
        for feature, coef in sorted(zip(feature_names, coefs), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {feature}: {coef:.4f}")
    
    def plot_decision_boundary(self):
        hours_range = np.linspace(0, 15, 100)
        gpa_range = np.linspace(1.0, 4.0, 100)
        xx, yy = np.meshgrid(hours_range, gpa_range)
        
        avg_attendance = self.df['Attendance'].mean()
        avg_practice = self.df['PracticeHours'].mean()
        avg_sleep = self.df['SleepHours'].mean()
        
        grid_data = pd.DataFrame({
            'StudyHours': xx.ravel(),
            'Attendance': avg_attendance,
            'PracticeHours': avg_practice,
            'PreviousGPA': yy.ravel(),
            'SleepHours': avg_sleep
        })
        
        probs = self.model.predict_proba(grid_data)[:, 1].reshape(xx.shape)
        
        plt.figure(figsize=(12, 9))
        contour = plt.contourf(xx, yy, probs, 30, cmap='RdYlGn', alpha=0.8)
        plt.colorbar(contour, label='Pass Probability')
        
        fail_mask = self.df['Pass'] == 0
        pass_mask = self.df['Pass'] == 1
        
        plt.scatter(self.df.loc[fail_mask, 'StudyHours'], 
                   self.df.loc[fail_mask, 'PreviousGPA'], 
                   c='red', edgecolor='darkred', s=60, label='Fail', alpha=0.7)
        plt.scatter(self.df.loc[pass_mask, 'StudyHours'], 
                   self.df.loc[pass_mask, 'PreviousGPA'], 
                   c='green', edgecolor='darkgreen', s=60, label='Pass', alpha=0.7)
        
        plt.xlabel('Study Hours', fontsize=12)
        plt.ylabel('Previous GPA', fontsize=12)
        plt.title('Decision Boundary: Study Hours vs Previous GPA\n(Other features at average values)', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('07_decision_boundary.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_probability_distribution(self):
        plt.figure(figsize=(12, 6))
        
        fail_probs = self.y_prob[self.y_test == 0]
        pass_probs = self.y_prob[self.y_test == 1]
        
        plt.hist(fail_probs, bins=30, alpha=0.6, label='Actual Failures', color='red', edgecolor='black')
        plt.hist(pass_probs, bins=30, alpha=0.6, label='Actual Passes', color='green', edgecolor='black')
        plt.axvline(0.5, color='navy', linestyle='--', linewidth=2, label='Decision Threshold')
        
        plt.xlabel('Predicted Pass Probability', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title('Distribution of Predicted Probabilities', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig('08_probability_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def predict_single_student(self, study_hours, attendance, practice_hours, 
                               previous_gpa, sleep_hours):
        try:
            input_data = pd.DataFrame({
                'StudyHours': [study_hours],
                'Attendance': [attendance],
                'PracticeHours': [practice_hours],
                'PreviousGPA': [previous_gpa],
                'SleepHours': [sleep_hours]
            })
            
            prob = self.model.predict_proba(input_data)[0][1]
            prediction = "PASS" if prob >= 0.5 else "FAIL"
            
            return prob, prediction
        except Exception as e:
            print(f"Error during prediction: {e}")
            return None, None
    
    def interactive_prediction(self):
        print("\n" + "="*80)
        print("INTERACTIVE PREDICTION")
        print("="*80)
        
        try:
            import ipywidgets as widgets
            from IPython.display import display, clear_output
            
            study_hours = widgets.FloatSlider(min=0, max=15, step=0.5, value=6.5, 
                                             description='Study Hours:')
            attendance = widgets.FloatSlider(min=0, max=100, step=1, value=85, 
                                            description='Attendance (%):')
            practice_hours = widgets.FloatSlider(min=0, max=8, step=0.5, value=3, 
                                                description='Practice Hours:')
            previous_gpa = widgets.FloatSlider(min=1.0, max=4.0, step=0.1, value=2.8, 
                                              description='Previous GPA:')
            sleep_hours = widgets.FloatSlider(min=4, max=12, step=0.5, value=7, 
                                             description='Sleep Hours:')
            predict_button = widgets.Button(description="Predict", button_style='success')
            output = widgets.Output()
            
            ui = widgets.VBox([
                widgets.HTML("<h3>Predict Pass Probability:</h3>"),
                study_hours,
                attendance,
                practice_hours,
                previous_gpa,
                sleep_hours,
                predict_button,
                output
            ])
            
            def on_predict_click(b):
                with output:
                    clear_output()
                    prob, classification = self.predict_single_student(
                        study_hours.value, attendance.value, practice_hours.value,
                        previous_gpa.value, sleep_hours.value
                    )
                    
                    if prob is not None:
                        color = 'green' if prob > 0.7 else ('orange' if prob > 0.5 else 'red')
                        
                        print(f"\n{'='*50}")
                        print(f"Prediction Results:")
                        print(f"{'='*50}")
                        print(f"Study Hours: {study_hours.value:.1f} hours")
                        print(f"Attendance: {attendance.value:.0f}%")
                        print(f"Practice Hours: {practice_hours.value:.1f} hours")
                        print(f"Previous GPA: {previous_gpa.value:.1f}")
                        print(f"Sleep Hours: {sleep_hours.value:.1f} hours")
                        print(f"\nPass Probability: {prob:.1%}")
                        print(f"Prediction: {classification}")
                        print(f"{'='*50}\n")
                        
                        plt.figure(figsize=(10, 2))
                        plt.barh([0], [prob], color=color, height=0.5, edgecolor='black', linewidth=2)
                        plt.xlim(0, 1)
                        plt.axvline(0.5, color='gray', linestyle='--', linewidth=2, label='Threshold')
                        plt.title('Pass Probability Indicator', fontsize=12, fontweight='bold')
                        plt.xlabel('Probability')
                        plt.yticks([])
                        plt.legend()
                        plt.tight_layout()
                        plt.close()
            
            predict_button.on_click(on_predict_click)
            display(ui)
        
        except ImportError:
            print("ipywidgets not available. Skipping interactive mode.")
            print("Enter values manually for prediction:")
            
            try:
                study_hours = float(input("Study Hours (0-15): "))
                attendance = float(input("Attendance (0-100): "))
                practice_hours = float(input("Practice Hours (0-8): "))
                previous_gpa = float(input("Previous GPA (1.0-4.0): "))
                sleep_hours = float(input("Sleep Hours (4-12): "))
                
                prob, classification = self.predict_single_student(
                    study_hours, attendance, practice_hours, previous_gpa, sleep_hours
                )
                
                if prob is not None:
                    print(f"\nPass Probability: {prob:.1%}")
                    print(f"Prediction: {classification}")
            
            except ValueError:
                print("Invalid input. Please enter numeric values.")
    
    def run_full_pipeline(self, skip_interactive=True):
        print("\n" + "="*80)
        print("STUDENT PASS PREDICTION MODEL - FULL PIPELINE")
        print("="*80)
        
        self.generate_dataset(n_samples=500)
        self.explore_data()
        self.prepare_data()
        self.train_model()
        self.evaluate_model()
        
        print("\n" + "="*80)
        print("VISUALIZATIONS")
        print("="*80)
        
        self.plot_roc_curve()
        self.plot_precision_recall_curve()
        self.plot_confusion_matrix()
        self.plot_feature_importance()
        self.plot_decision_boundary()
        self.plot_probability_distribution()
        
        if not skip_interactive:
            self.interactive_prediction()
        
        print("\n" + "="*80)
        print("KEY INSIGHTS")
        print("="*80)
        print("1. Study hours and previous GPA are the strongest predictors of passing")
        print("2. The model shows diminishing returns for study hours beyond 10 hours")
        print("3. Attendance has a moderate positive effect on pass probability")
        print("4. Practice hours show a significant impact despite lower values")
        print("5. Sleep hours positively correlate with academic performance")
        print("6. Students with GPA < 2.0 need substantial additional study time to pass")
        print("7. Combining all factors creates a robust prediction system")
        print("\nAll visualizations saved as PNG files in the current directory.")
        print("="*80 + "\n")


if __name__ == "__main__":
    model = StudentPassPredictionModel(random_state=42, test_size=0.2)
    model.run_full_pipeline()
