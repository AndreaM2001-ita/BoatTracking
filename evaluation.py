import os
from ultralytics import YOLO
import numpy as np
import yaml


def evaluate_model(model_path, dataset_path):
    # Load current model
    model = YOLO(model_path)
    
    # Run validation 
    results = model.val(data=dataset_path)
    print("--------------------------------")



def evaluate_models_in_folder(folder_path, dataset_path):
    all_metrics = {}

    # Find all model files in the folder 
    model_files = [f for f in os.listdir(folder_path) if f.endswith('.pt')]
    
    # Evaluate models
    for model_file in model_files:
        model_path = os.path.join(folder_path, model_file)
        print(f"Evaluating model: {model_path}")
        metrics = evaluate_model(model_path, dataset_path)
        all_metrics[model_file] = metrics
    
    return all_metrics


models_folder = 'trainedModels'  # YOLOv8 Model folder


dataset_pathFile = 'config.yaml'  # dataset path

try:
    
    evaluation_results = evaluate_models_in_folder(models_folder, dataset_pathFile)

    # Display the evaluation results
    for model_name, metrics in evaluation_results.items():
        print(f"Metrics for {model_name}:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")

except yaml.YAMLError as e:
    print("If there are errors related to the YAML file, please verify the file path. Manually copy the complete path to the YAML file and paste it in the 'path' attribute of your configuration file.")