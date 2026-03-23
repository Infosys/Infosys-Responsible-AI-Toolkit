''' 
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
fileName: local_constants.py
description: Local constants for usecase  module
"""

DELTED_SUCCESS_MESSAGE="Successfully deleted the usecase :"
USECASE_ALREADY_EXISTS= "Usecase with name PLACEHOLDER_TEXT already exists"
USECASE_NOT_FOUND_ERROR="Usecase id PLACEHOLDER_TEXT Not Found"
USECASE_NAME_VALIDATION_ERROR="Usecase name should not be empty"
SPACE_DELIMITER=" "
PLACEHOLDER_TEXT="PLACEHOLDER_TEXT"

#Method Descriptions
ANCHOR_TABULAR_DES= "Anchor interpretability technique is a model-agnostic method extending Local Interpretable Model-agnostic Explanations (LIME) for explaining individual predictions made by any machine learning model. The idea behind Anchors is to create a simple, human-interpretable rule that approximates the model's behavior within a specific context. An Anchor explanations rule that sufficiently 'anchors' the prediction locally - such that changes to the rest of the feature values of the instance do not change the prediction."
LOCAL_KERNEL_SHAP_DES="Kernel SHAP (SHapley Additive exPlanations) interpretability technique explains the impact of each feature on a model's prediction. Local explanation output from Kernel SHAP provides a detailed breakdown of feature contributions to a specific prediction, showing how each feature influences the model's output for that instance. It offers a clear understanding of why the model made a particular prediction for a single data point."
GLOBAL_KERNEL_SHAP_DES="Global Kernel SHAP is a method for explaining the output of any machine learning model on a global scale. It summarizes the overall importance of each feature across all predictions in the dataset. Also, provides a comprehensive view of the model's behavior by highlighting which features have the most significant impact on its decisions. Global Kernel SHAP explanations offer a high-level overview, complementing the local explanations to provide a holistic understanding of the model's behavior."
LOCAL_TREE_SHAP_DES="Tree SHAP is a method for explaining the output of tree-based machine learning models. It uses Shapley values, a concept from cooperative game theory, to allocate a fair contribution to each feature in making the prediction. Tree SHAP focuses on explaining how each feature affects the model's output for an individual prediction."
GLOBAL_TREE_SHAP_DES="Global Tree SHAP is a method for explaining the output of tree-based machine learning models on a global scale. Global Tree SHAP provides an overview of the overall importance of each feature in a tree-based model across all predictions in the dataset. It aggregates the local explanations from each instance to calculate the average impact of each feature on the model's output."
LIME_TABULAR_DES="LIME (Local Interpretable Model-Agnostic Explanations) provide insights into individual predictions by approximating the model's behavior around a specific instance using a simple, interpretable model. LIME generates explanations by perturbing the features of the instance of interest and observing the changes in the model's predictions. This process helps identify which features are most influential for a particular prediction, making the model's decision more transparent and understandable."
GLOBAL_PD_VARIANCE_DES="Partial Dependence Variance is a technique used to understand the importance of features in a machine learning model.This method calculates a single positive number that represents the importance of a feature or the interaction between two features.The method is based on the concept of Partial Dependence (PD), which shows how changes in a feature's value affect the model's predictions. The variance within the PD function is used to quantify the feature's importance.In simpler terms, if a feature has a high variance in its PD function, it means that changes in this feature's value can cause significant changes in the model's predictions, indicating that the feature is important."
GLOBAL_PERMUTATION_IMPORTANCE_DES="Permutation importance is a technique used to determine the importance of features in a machine learning model.The idea behind permutation importance is to measure the decrease in a model's performance when the values of a feature are randomly shuffled. This shuffling breaks the relationship between the feature and the target, so any decrease in model performance indicates that the feature is important.In other words, if the model's accuracy drops significantly when the values of a feature are permuted, it suggests that the model relies heavily on this feature for making predictions, indicating that the feature is important."
LOCAL_TS_LIME_EXPLAINER_DES="LimeTimeSeries works by treating individual time steps or sequences of time steps as features. It changes these 'features' to create a group of similar time series, and then builds a local model on this group to explain the original model's prediction. LimeTimeSeries explanations as importance scores for each feature (time step or sequence of time steps), showing how much each one affects the prediction. This helps you see which parts of the time series have the biggest impact on the model's predictions."
INTEGRATED_GRADIENT_DES="Integrated Gradients is a technique used to explain how a machine learning model makes its predictions. It helps us understand which parts of the input (like features of the data) are most important for the model's decision. The method works by gradually changing the input from a baseline (usually zero) to the actual input and measuring how the model's output changes. This way, it gives us a clear picture of how each part of the input contributes to the final prediction, making complex models easier to understand for everyone."

# How to read explanation
ANCHOR_EXPLANATION = "An anchor explanation is a type of rule that provides a stable basis for a prediction in a local context. This means that even if other feature values of the instance change, the prediction remains the same due to the influence of these 'anchor' features."
INTEGRATED_GRADIENT_EXPLANATION = "Integrated Gradients is a method that attributes the model's prediction to the input features. It calculates the contribution of each feature to the model's decision by integrating the gradients of the model's output with respect to the input features along the path from a baseline input to the actual input. The higher the value, the more important the feature is in the model's decision."
FEATURE_IMPORTANCE_EXPLANATION = "The graph shows the importance of each feature in the model's decision. The importance score is a measure of how much each feature contributes to the model's decision. The higher the score, the more important the feature is. The graph is sorted in descending order, with the most important feature at the top."
FEATURE_IMPORTANCE_GLOBAL_EXPLANATION = "The graphs below show the importance of each feature in the model's decision for each class and overall importance of features aggregated for all the classes. The importance score is a measure of how much each feature contributes to the model's decision. The higher the score, the more important the feature is. The graph is sorted in descending order, with the most important feature at the top."
