from typing import List
from ..core.models import StoryPrompt, StoryAnalysis, StoryGap, StoryQuestion
from ..core.llm_interface import LLMInterface

class StoryAnalyzer:
    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def analyze_story(self, prompt: StoryPrompt) -> StoryAnalysis:
        system_prompt = """You are an expert story analyst. Analyze the given story prompt and identify:
1. Gaps or missing elements that need clarification
2. Questions that would help develop the story
3. Strengths of the current concept
4. Genre analysis and complexity assessment

Be thorough but constructive in your analysis."""

        analysis_prompt = f"""
Analyze this story prompt:

Story Type: {prompt.story_type}
Content: {prompt.content}
Genre: {prompt.genre or 'Not specified'}
Target Length: {prompt.target_length or 'Not specified'}
Style Preferences: {prompt.style_preferences or 'Not specified'}

Identify gaps, generate clarifying questions, note strengths, and assess complexity.
"""

        schema = {
            "type": "object",
            "properties": {
                "gaps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "category": {"type": "string"},
                            "severity": {"type": "integer", "minimum": 1, "maximum": 5},
                            "related_questions": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["description", "category", "severity"]
                    }
                },
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "category": {"type": "string"},
                            "importance": {"type": "integer", "minimum": 1, "maximum": 5},
                            "suggested_answer": {"type": "string"}
                        },
                        "required": ["question", "category", "importance"]
                    }
                },
                "strengths": {"type": "array", "items": {"type": "string"}},
                "genre_analysis": {"type": "string"},
                "complexity_score": {"type": "integer", "minimum": 1, "maximum": 10}
            },
            "required": ["gaps", "questions", "strengths", "complexity_score"]
        }

        result = self.llm.generate_structured(analysis_prompt, schema, system_prompt)

        gaps = [StoryGap(**gap) for gap in result["gaps"]]
        questions = [StoryQuestion(**q) for q in result["questions"]]

        return StoryAnalysis(
            gaps=gaps,
            questions=questions,
            strengths=result["strengths"],
            genre_analysis=result.get("genre_analysis"),
            complexity_score=result["complexity_score"]
        )

    def generate_follow_up_questions(self, analysis: StoryAnalysis,
                                   user_answers: dict) -> List[StoryQuestion]:
        system_prompt = """Generate additional clarifying questions based on the user's previous answers.
Focus on areas that still need development or where answers revealed new gaps."""

        prompt = f"""
Based on this analysis and user answers, generate follow-up questions:

Original Analysis: {analysis.model_dump_json(indent=2)}
User Answers: {user_answers}

Generate 3-5 targeted follow-up questions.
"""

        schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "category": {"type": "string"},
                            "importance": {"type": "integer", "minimum": 1, "maximum": 5}
                        },
                        "required": ["question", "category", "importance"]
                    }
                }
            },
            "required": ["questions"]
        }

        result = self.llm.generate_structured(prompt, schema, system_prompt)
        return [StoryQuestion(**q) for q in result["questions"]]