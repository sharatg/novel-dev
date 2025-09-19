from typing import List, Optional
from ..core.models import StoryContext, CritiqueResult
from ..core.llm_interface import LLMInterface
from ..core.context_manager import ContextManager

class StoryCritic:
    def __init__(self, llm: LLMInterface, context_manager: ContextManager):
        self.llm = llm
        self.context_manager = context_manager

    def critique_chapter(self, chapter_content: str, chapter_index: int,
                        context: StoryContext) -> CritiqueResult:
        chapter = context.outline.chapters[chapter_index]

        system_prompt = """You are a professional story editor and critic. Provide constructive,
detailed feedback on story chapters focusing on:

1. Character development and consistency
2. Plot advancement and coherence
3. Writing quality and style
4. Pacing and structure
5. Continuity with previous chapters
6. Genre conventions and reader expectations

Be specific, actionable, and balanced in your critique."""

        critique_prompt = f"""
Critique this chapter:

Chapter {chapter_index + 1}: {chapter.title}
Expected Summary: {chapter.summary}
Expected Key Events: {', '.join(chapter.key_events)}

Chapter Content:
{chapter_content}

Story Context:
- Genre: {context.outline.genre}
- Theme: {context.outline.theme}
- Setting: {context.outline.setting}

Previous chapters summary:
{self.context_manager.get_recent_content(2)[:1000] if chapter_index > 0 else "This is the first chapter"}

Character arcs so far:
{self.context_manager.get_character_summary()[:1000]}

Provide detailed critique focusing on strengths, weaknesses, and specific suggestions.
"""

        schema = {
            "type": "object",
            "properties": {
                "overall_score": {"type": "integer", "minimum": 1, "maximum": 10},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "suggestions": {"type": "array", "items": {"type": "string"}},
                "continuity_issues": {"type": "array", "items": {"type": "string"}},
                "character_consistency": {"type": "integer", "minimum": 1, "maximum": 10},
                "plot_coherence": {"type": "integer", "minimum": 1, "maximum": 10}
            },
            "required": ["overall_score", "strengths", "weaknesses", "suggestions",
                        "character_consistency", "plot_coherence"]
        }

        result = self.llm.generate_structured(critique_prompt, schema, system_prompt)

        return CritiqueResult(
            overall_score=result["overall_score"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            suggestions=result["suggestions"],
            continuity_issues=result.get("continuity_issues", []),
            character_consistency=result["character_consistency"],
            plot_coherence=result["plot_coherence"]
        )

    def critique_full_story(self, context: StoryContext) -> CritiqueResult:
        system_prompt = """You are a professional story editor reviewing a complete work.
Evaluate the overall narrative structure, character arcs, thematic coherence, and
writing quality across the entire story."""

        full_content = "\n\n".join(context.completed_chapters)

        critique_prompt = f"""
Review this complete story:

Title: {context.outline.title}
Genre: {context.outline.genre}
Theme: {context.outline.theme}

Full Story Content:
{full_content[:5000]}...

Story Outline:
{context.outline.model_dump_json(indent=2)}

Evaluate the complete work for:
1. Overall narrative coherence
2. Character arc completion
3. Thematic consistency
4. Pacing and structure
5. Genre satisfaction
6. Writing quality consistency

Provide comprehensive feedback on the finished work.
"""

        schema = {
            "type": "object",
            "properties": {
                "overall_score": {"type": "integer", "minimum": 1, "maximum": 10},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "suggestions": {"type": "array", "items": {"type": "string"}},
                "continuity_issues": {"type": "array", "items": {"type": "string"}},
                "character_consistency": {"type": "integer", "minimum": 1, "maximum": 10},
                "plot_coherence": {"type": "integer", "minimum": 1, "maximum": 10}
            },
            "required": ["overall_score", "strengths", "weaknesses", "suggestions",
                        "character_consistency", "plot_coherence"]
        }

        result = self.llm.generate_structured(critique_prompt, schema, system_prompt)

        return CritiqueResult(
            overall_score=result["overall_score"],
            strengths=result["strengths"],
            weaknesses=result["weaknesses"],
            suggestions=result["suggestions"],
            continuity_issues=result.get("continuity_issues", []),
            character_consistency=result["character_consistency"],
            plot_coherence=result["plot_coherence"]
        )

    def suggest_improvements(self, chapter_content: str, critique: CritiqueResult) -> str:
        system_prompt = """Based on the critique provided, suggest specific textual improvements
to the chapter. Focus on the most important issues identified in the critique."""

        improvement_prompt = f"""
Chapter Content:
{chapter_content[:2000]}

Critique Results:
- Overall Score: {critique.overall_score}/10
- Weaknesses: {', '.join(critique.weaknesses)}
- Suggestions: {', '.join(critique.suggestions)}
- Continuity Issues: {', '.join(critique.continuity_issues)}

Provide specific, actionable suggestions for improving this chapter.
Focus on the 3-5 most important improvements that would have the biggest impact.
"""

        return self.llm.generate(improvement_prompt, system_prompt, temperature=0.6)

    def check_continuity(self, context: StoryContext, num_recent_chapters: int = 5) -> List[str]:
        system_prompt = """Check for continuity errors, inconsistencies, and plot holes
across the recent chapters. Focus on character behavior, timeline, world-building,
and plot thread consistency."""

        recent_content = self.context_manager.get_recent_content(num_recent_chapters)
        if not recent_content:
            return []

        continuity_prompt = f"""
Check these recent chapters for continuity issues:

Story Context:
- Characters: {self.context_manager.get_character_summary()[:1000]}
- Plot Status: {self.context_manager.get_plot_summary()[:1000]}

Recent Chapter Content:
{recent_content[:3000]}

Identify any:
1. Character behavior inconsistencies
2. Timeline or chronology errors
3. World-building contradictions
4. Forgotten or contradicted plot points
5. Inconsistent character knowledge or relationships

List specific continuity issues found.
"""

        schema = {
            "type": "object",
            "properties": {
                "continuity_issues": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["continuity_issues"]
        }

        result = self.llm.generate_structured(continuity_prompt, schema, system_prompt)
        return result["continuity_issues"]