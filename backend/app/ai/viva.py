"""
Viva Question Generator.

Rule-based template generation, parameterized with facts extracted
elsewhere in the pipeline (title, keywords, algorithms, datasets, metrics,
contributions, gaps). This produces relevant, paper-specific questions
without needing a generative LLM — a common, defensible technique for
"exam question" generators.
"""
from typing import Dict, List


def _fill(templates: List[str], **kwargs) -> List[str]:
    out = []
    for t in templates:
        try:
            out.append(t.format(**kwargs))
        except (KeyError, IndexError):
            continue
    return out


def generate_viva_questions(
    title: str,
    keywords: List[str],
    methodology: Dict,
    contributions: List[str],
    gaps: List[str],
    min_per_level: int = 10,
) -> Dict[str, List[str]]:

    algorithms = methodology.get("algorithms") or ["the proposed method"]
    datasets = methodology.get("datasets") or ["the dataset used in this study"]
    metrics = methodology.get("evaluation_metrics") or ["the reported evaluation metric"]
    kw = keywords or ["the core concept of this paper"]

    easy_templates = [
        "What is the title of this research paper?",
        "What problem does this paper, '{title}', try to solve?",
        "What is {kw0}?",
        "What is {kw1}?",
        "Which dataset was used in this research?",
        "Name one algorithm or model used in this paper.",
        "What does the abstract of this paper say the goal is?",
        "What field or domain does this research belong to?",
        "What is the main topic discussed in the introduction?",
        "List two keywords associated with this paper.",
        "What type of paper is this — experimental, theoretical, or survey?",
        "Who would benefit from reading this paper?",
    ]

    medium_templates = [
        "Explain how {algo0} works in the context of this paper.",
        "Why was the {dataset0} used for this study?",
        "What evaluation metric(s) did the authors use, and why?",
        "Summarize the methodology used in '{title}'.",
        "What are the key steps in the proposed pipeline?",
        "How does this paper's approach differ from traditional methods?",
        "What preprocessing steps, if any, were applied to the data?",
        "Explain the significance of {metric0} in evaluating this work.",
        "What tools or frameworks would you use to reproduce this work?",
        "Describe one contribution of this paper in your own words.",
        "What assumptions does the proposed method rely on?",
        "How is the training/validation/testing split typically handled in this kind of study?",
    ]

    hard_templates = [
        "Critically evaluate the choice of {algo0} over alternative approaches.",
        "What are the potential limitations of using {dataset0} for this problem?",
        "How would you improve the methodology proposed in this paper?",
        "Discuss the trade-offs between accuracy and computational cost in this approach.",
        "What is a known research gap this paper does not fully address: '{gap0}'?",
        "How would you design an ablation study to validate this paper's claims?",
        "What ethical or fairness concerns, if any, apply to this research?",
        "How sensitive do you think the results are to hyperparameter choices?",
        "Propose an alternative evaluation metric and justify it over {metric0}.",
        "How would this method scale to a much larger dataset?",
        "What would happen if {dataset0} had significant class imbalance?",
        "Compare this paper's contribution to the broader state of the art.",
    ]

    professor_templates = [
        "Derive or justify, at a conceptual level, why {algo0} is theoretically suited to this problem.",
        "If you were the reviewer, what is the single most important weakness you'd flag in this paper?",
        "How would you redesign the experiments to make the results more statistically robust?",
        "What novel research direction would you propose as a direct extension of: '{gap0}'?",
        "Defend the paper's contribution against the criticism that it is incremental.",
        "What would a failure analysis of this method likely reveal?",
        "How generalizable are these findings outside of {dataset0}?",
        "What is the theoretical upper bound on performance for this kind of task, if any?",
        "How would you position this paper's contribution relative to a completely different methodological paradigm?",
        "If given unlimited compute and data, how would you redesign this study from scratch?",
        "What publication-quality experiment is missing from this paper?",
        "How would you defend this paper's novelty in a live thesis defense?",
    ]

    fmt_kwargs = dict(
        title=title or "this paper",
        kw0=kw[0] if len(kw) > 0 else "the main concept",
        kw1=kw[1] if len(kw) > 1 else "a key term from the paper",
        algo0=algorithms[0],
        dataset0=datasets[0],
        metric0=metrics[0],
        gap0=(gaps[0] if gaps else "an open problem in this field"),
    )

    result = {
        "easy": _fill(easy_templates, **fmt_kwargs)[:min_per_level],
        "medium": _fill(medium_templates, **fmt_kwargs)[:min_per_level],
        "hard": _fill(hard_templates, **fmt_kwargs)[:min_per_level],
        "professor_level": _fill(professor_templates, **fmt_kwargs)[:min_per_level],
    }
    return result
