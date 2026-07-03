"""
Methodology Breakdown.

Extracts, using dictionary + regex matching against the Methodology /
Experiments / Results sections:
  - Datasets used (matched against a curated list of common public datasets
    plus a generic "<Word>+ dataset" pattern to catch unseen ones)
  - Algorithms / models used (curated list of common ML/DL/NLP/CV algorithm
    names plus generic capitalized-acronym detection)
  - Evaluation metrics (curated list: accuracy, F1, precision, recall, etc.)
  - A step-by-step pipeline summary, built from the ordered set of
    methodology sentences that contain process verbs (e.g. "we first...",
    "then", "finally").
This is deterministic, explainable, and requires no paid LLM.
"""
import re
from typing import Dict, List

from app.ai.model_manager import get_spacy_model

KNOWN_DATASETS = [
    "MNIST", "CIFAR-10", "CIFAR-100", "ImageNet", "COCO", "Pascal VOC",
    "SQuAD", "GLUE", "SuperGLUE", "IMDB", "Amazon Reviews", "Yelp",
    "Wikipedia", "Common Crawl", "WMT", "CoNLL", "Penn Treebank",
    "MS MARCO", "Kaggle", "UCI", "KITTI", "Cityscapes", "CelebA",
    "LFW", "VGGFace", "Reuters", "20 Newsgroups", "Twitter", "Reddit",
    "arXiv", "PubMed", "MIMIC", "UCF101", "Kinetics", "AudioSet",
]

KNOWN_ALGORITHMS = [
    "CNN", "RNN", "LSTM", "GRU", "Transformer", "BERT", "GPT", "ResNet",
    "VGG", "AlexNet", "YOLO", "Faster R-CNN", "U-Net", "GAN", "VAE",
    "Random Forest", "SVM", "XGBoost", "LightGBM", "Decision Tree",
    "K-Means", "Naive Bayes", "Logistic Regression", "Linear Regression",
    "Autoencoder", "Attention", "Reinforcement Learning", "Q-Learning",
    "Gradient Boosting", "KNN", "PCA", "BiLSTM", "Seq2Seq", "GCN", "GNN",
    "Word2Vec", "GloVe", "TF-IDF", "Bagging", "AdaBoost",
]

KNOWN_METRICS = [
    "Accuracy", "Precision", "Recall", "F1-score", "F1 Score", "AUC", "ROC",
    "Mean Squared Error", "MSE", "RMSE", "MAE", "BLEU", "ROUGE", "Perplexity",
    "IoU", "mAP", "Top-1 Accuracy", "Top-5 Accuracy", "Confusion Matrix",
    "Sensitivity", "Specificity", "R-squared", "Log Loss", "Cohen's Kappa",
]

PIPELINE_CUES = [
    "first", "initially", "then", "next", "after", "subsequently",
    "finally", "we begin by", "the process starts", "the pipeline consists of",
]


def _find_matches(text: str, vocabulary: List[str]) -> List[str]:
    found = []
    lowered = text.lower()
    for term in vocabulary:
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, lowered):
            found.append(term)
    return sorted(set(found))


def _extract_pipeline_steps(text: str, max_steps: int = 8) -> List[str]:
    nlp = get_spacy_model()
    doc = nlp(text)
    steps = []
    for sent in doc.sents:
        s = sent.text.strip()
        if 20 < len(s) < 300 and any(cue in s.lower() for cue in PIPELINE_CUES):
            steps.append(s)
        if len(steps) >= max_steps:
            break
    return steps


def extract_methodology(sections: Dict[str, str]) -> Dict:
    text = " ".join([
        sections.get("methodology", ""),
        sections.get("experiments", ""),
        sections.get("results", ""),
    ])
    if not text.strip():
        text = sections.get("body", "")

    datasets = _find_matches(text, KNOWN_DATASETS)
    algorithms = _find_matches(text, KNOWN_ALGORITHMS)
    metrics = _find_matches(text, KNOWN_METRICS)
    pipeline_steps = _extract_pipeline_steps(sections.get("methodology", "") or text)

    return {
        "datasets": datasets,
        "algorithms": algorithms,
        "evaluation_metrics": metrics,
        "pipeline_steps": pipeline_steps,
    }
