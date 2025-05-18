from dataclasses import dataclass


@dataclass
class Competency:
    name: str
    description: str
    similarity_score: float


@dataclass
class CourseRecommendation:
    title: str
    relevance_explanation: str
