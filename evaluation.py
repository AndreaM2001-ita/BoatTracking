import os
from ultralytics import YOLO
import numpy as np
import yaml

# Function to evaluate a model on a dataset and return metrics
def evaluate_model(model_path, dataset_path):
    # Load YOLOv8 model
    model = YOLO(model_path)
    
    # Run validation on the dataset
    results = model.val(data=dataset_path)
    print("--------------------------------")
    # Extract evaluation metrics


# Function to evaluate all models in a folder
def evaluate_models_in_folder(folder_path, dataset_path):
    all_metrics = {}

    # Find all model files in the folder with .pt extension
    model_files = [f for f in os.listdir(folder_path) if f.endswith('.pt')]
    
    # Evaluate each model
    for model_file in model_files:
        model_path = os.path.join(folder_path, model_file)
        print(f"Evaluating model: {model_path}")
        metrics = evaluate_model(model_path, dataset_path)
        all_metrics[model_file] = metrics
    
    return all_metrics

# Path to folder containing YOLOv8 models
models_folder = 'trainedModels'  # Replace with your folder path

# Path to your dataset (dataset.yaml or a directory with images and labels)
dataset_pathFile = 'config.yaml'  # Replace with your dataset path

# Load and evaluate the models, handling potential YAML file errors
try:
    
    # Evaluate all models in the folder and print metrics
    evaluation_results = evaluate_models_in_folder(models_folder, dataset_pathFile)

    # Display the evaluation results
    for model_name, metrics in evaluation_results.items():
        print(f"Metrics for {model_name}:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")

except yaml.YAMLError as e:
    print("If there are errors related to the YAML file, please verify the file path. Manually copy the complete path to the YAML file and paste it in the 'path' attribute of your configuration file.")