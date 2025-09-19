from typing import Dict, Any
from ..core.models import StoryPrompt, StoryAnalysis, StoryOutline, Chapter
from ..core.llm_interface import LLMInterface

class OutlineCreator:
    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def create_outline(self, prompt: StoryPrompt, analysis: StoryAnalysis,
                      user_answers: Dict[str, Any]) -> StoryOutline:
        system_prompt = """You are an expert story planner. Create a detailed, well-structured outline
based on the story prompt, analysis, and user's answers to clarifying questions.

For novels: Create 15-25 chapters with 2000-4000 words each
For screenplays: Create acts and scenes with appropriate pacing
For short stories: Create 3-7 sections with 500-1500 words each

Ensure proper story structure, character development, and pacing."""

        outline_prompt = f"""
Create a detailed outline for this story:

Original Prompt: {prompt.content}
Story Type: {prompt.story_type}
Target Length: {prompt.target_length or 'Standard length'}
Genre: {prompt.genre or 'To be determined'}

Analysis Insights:
- Complexity Score: {analysis.complexity_score}/10
- Key Strengths: {', '.join(analysis.strengths)}
- Genre Analysis: {analysis.genre_analysis or 'Not provided'}

User Answers to Questions:
{self._format_user_answers(user_answers)}

Create a comprehensive outline with:
1. Clear title and premise
2. Main theme
3. Well-developed main characters with arcs
4. Detailed setting
5. Chapter-by-chapter breakdown with titles, summaries, key events, and characters
6. Appropriate word count targets
"""

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "premise": {"type": "string"},
                "theme": {"type": "string"},
                "main_characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "description": {"type": "string"},
                            "arc": {"type": "string"},
                            "motivation": {"type": "string"}
                        },
                        "required": ["name", "role", "description"]
                    }
                },
                "setting": {"type": "string"},
                "chapters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                            "key_events": {"type": "array", "items": {"type": "string"}},
                            "characters_involved": {"type": "array", "items": {"type": "string"}},
                            "word_count_target": {"type": "integer"}
                        },
                        "required": ["title", "summary", "key_events", "characters_involved", "word_count_target"]
                    }
                },
                "total_word_count": {"type": "integer"},
                "genre": {"type": "string"}
            },
            "required": ["title", "premise", "theme", "main_characters", "setting", "chapters", "total_word_count", "genre"]
        }

        result = self.llm.generate_structured(outline_prompt, schema, system_prompt)

        chapters = [Chapter(**chapter) for chapter in result["chapters"]]

        return StoryOutline(
            title=result["title"],
            premise=result["premise"],
            theme=result["theme"],
            main_characters=result["main_characters"],
            setting=result["setting"],
            chapters=chapters,
            total_word_count=result["total_word_count"],
            genre=result["genre"]
        )

    def revise_outline(self, outline: StoryOutline, feedback: str) -> StoryOutline:
        system_prompt = """Revise the story outline based on user feedback.
Maintain the overall structure while incorporating the requested changes.
Ensure consistency across all chapters and character arcs."""

        revision_prompt = f"""
Revise this outline based on the feedback:

Current Outline: {outline.model_dump_json(indent=2)}

User Feedback: {feedback}

Provide the complete revised outline maintaining structural integrity.
"""

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "premise": {"type": "string"},
                "theme": {"type": "string"},
                "main_characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "description": {"type": "string"},
                            "arc": {"type": "string"},
                            "motivation": {"type": "string"}
                        },
                        "required": ["name", "role", "description"]
                    }
                },
                "setting": {"type": "string"},
                "chapters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                            "key_events": {"type": "array", "items": {"type": "string"}},
                            "characters_involved": {"type": "array", "items": {"type": "string"}},
                            "word_count_target": {"type": "integer"}
                        },
                        "required": ["title", "summary", "key_events", "characters_involved", "word_count_target"]
                    }
                },
                "total_word_count": {"type": "integer"},
                "genre": {"type": "string"}
            },
            "required": ["title", "premise", "theme", "main_characters", "setting", "chapters", "total_word_count", "genre"]
        }

        result = self.llm.generate_structured(revision_prompt, schema, system_prompt)
        chapters = [Chapter(**chapter) for chapter in result["chapters"]]

        return StoryOutline(
            title=result["title"],
            premise=result["premise"],
            theme=result["theme"],
            main_characters=result["main_characters"],
            setting=result["setting"],
            chapters=chapters,
            total_word_count=result["total_word_count"],
            genre=result["genre"]
        )

    def _format_user_answers(self, answers: Dict[str, Any]) -> str:
        formatted = []
        for question, answer in answers.items():
            formatted.append(f"Q: {question}\nA: {answer}")
        return "\n\n".join(formatted)