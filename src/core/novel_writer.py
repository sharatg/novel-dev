from typing import Dict, Any, Optional, List
import os
from ..core.models import StoryPrompt, StoryContext, StoryOutline
from ..core.llm_interface import LLMInterface
from ..core.context_manager import ContextManager
from ..agents.story_analyzer import StoryAnalyzer
from ..agents.outline_creator import OutlineCreator
from ..agents.writing_engine import WritingEngine
from ..agents.story_critic import StoryCritic

class NovelWriter:
    def __init__(self, project_name: str, project_dir: str = "./projects"):
        self.project_name = project_name
        self.project_path = os.path.join(project_dir, project_name)

        self.llm = LLMInterface()
        self.context_manager = ContextManager(self.project_path)

        self.analyzer = StoryAnalyzer(self.llm)
        self.outline_creator = OutlineCreator(self.llm)
        self.writing_engine = WritingEngine(self.llm, self.context_manager)
        self.critic = StoryCritic(self.llm, self.context_manager)

    def check_llm_availability(self) -> bool:
        return self.llm.is_available()

    def start_new_project(self, prompt: StoryPrompt) -> Dict[str, Any]:
        if not self.check_llm_availability():
            raise Exception("Local LLM is not available. Please ensure Ollama is running and the model is installed.")

        analysis = self.analyzer.analyze_story(prompt)

        # Save the initial project state with prompt and analysis
        initial_context = {
            "prompt": prompt.model_dump(),
            "analysis": analysis.model_dump(),
            "stage": "questions"
        }

        # Save to a temporary file until outline is created
        import json
        temp_file = os.path.join(self.project_path, "temp_project_state.json")
        with open(temp_file, 'w') as f:
            json.dump(initial_context, f, indent=2)

        return {
            "analysis": analysis,
            "questions": analysis.questions,
            "gaps": analysis.gaps,
            "strengths": analysis.strengths
        }

    def answer_questions(self, answers: Dict[str, str]) -> StoryOutline:
        # Try to load existing context first
        context = self.context_manager.load_context()

        if not context:
            # Load from temporary project state
            import json
            temp_file = os.path.join(self.project_path, "temp_project_state.json")

            if not os.path.exists(temp_file):
                raise Exception("No active project found. Please start a new project first.")

            with open(temp_file, 'r') as f:
                temp_state = json.load(f)

            # Reconstruct the original prompt and analysis
            prompt = StoryPrompt(**temp_state["prompt"])

            # Reconstruct the analysis object
            from ..core.models import StoryAnalysis, StoryGap, StoryQuestion
            analysis_data = temp_state["analysis"]
            gaps = [StoryGap(**gap) for gap in analysis_data["gaps"]]
            questions = [StoryQuestion(**q) for q in analysis_data["questions"]]

            analysis = StoryAnalysis(
                gaps=gaps,
                questions=questions,
                strengths=analysis_data["strengths"],
                genre_analysis=analysis_data.get("genre_analysis"),
                complexity_score=analysis_data["complexity_score"]
            )
        else:
            # This shouldn't happen in normal flow, but handle it
            raise Exception("Project already has an outline. Use revision methods instead.")

        outline = self.outline_creator.create_outline(prompt, analysis, answers)

        # Create and save proper story context
        story_context = StoryContext(
            outline=outline,
            plot_threads={
                "main_plot": "Beginning",
                "character_development": "Initial setup"
            }
        )
        self.context_manager.save_context(story_context)

        # Clean up temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return outline

    def approve_outline(self, approved: bool, feedback: Optional[str] = None) -> Optional[StoryOutline]:
        if approved:
            return None  # Outline is approved, ready to start writing

        if not feedback:
            raise ValueError("Feedback is required when outline is not approved")

        context = self.context_manager.load_context()
        if not context:
            raise Exception("No active project found")

        revised_outline = self.outline_creator.revise_outline(context.outline, feedback)
        context.outline = revised_outline
        self.context_manager.save_context(context)

        return revised_outline

    def write_next_chapter(self, additional_instructions: Optional[str] = None) -> Dict[str, Any]:
        context = self.context_manager.load_context()
        if not context:
            raise Exception("No active project found")

        if context.current_chapter >= len(context.outline.chapters):
            return {"completed": True, "message": "Story is complete!"}

        chapter_content = self.writing_engine.write_chapter(
            context.current_chapter, context, additional_instructions
        )

        # Critique the chapter
        critique = self.critic.critique_chapter(
            chapter_content, context.current_chapter, context
        )

        return {
            "completed": False,
            "chapter_index": context.current_chapter,
            "chapter_title": context.outline.chapters[context.current_chapter].title,
            "content": chapter_content,
            "critique": critique,
            "word_count": len(chapter_content.split())
        }

    def finalize_chapter(self, approved: bool, revisions: Optional[str] = None) -> None:
        context = self.context_manager.load_context()
        if not context:
            raise Exception("No active project found")

        # Get the latest chapter content
        sessions = self.context_manager.load_sessions()
        if not sessions:
            raise Exception("No chapter content found")

        latest_session = sessions[-1]
        chapter_content = latest_session["content_written"]

        if not approved and revisions:
            # Apply revisions
            chapter_content = self.apply_revisions(chapter_content, revisions, context)

        # Finalize the chapter
        self.writing_engine.finalize_chapter(
            context.current_chapter, chapter_content, context
        )

    def apply_revisions(self, content: str, revision_notes: str, context: StoryContext) -> str:
        system_prompt = """Apply the requested revisions to this chapter content.
Maintain the overall structure and story elements while addressing the specific
revision requests."""

        revision_prompt = f"""
Original Chapter Content:
{content}

Revision Notes:
{revision_notes}

Apply the requested revisions while maintaining story consistency and quality.
Return the complete revised chapter.
"""

        return self.llm.generate(revision_prompt, system_prompt, temperature=0.7)

    def get_story_status(self) -> Dict[str, Any]:
        context = self.context_manager.load_context()
        if not context:
            return {"error": "No active project found"}

        total_chapters = len(context.outline.chapters)
        completed_chapters = len(context.completed_chapters)

        total_words = sum(len(chapter.split()) for chapter in context.completed_chapters)

        return {
            "title": context.outline.title,
            "genre": context.outline.genre,
            "progress": {
                "chapters_completed": completed_chapters,
                "total_chapters": total_chapters,
                "percentage": (completed_chapters / total_chapters) * 100,
                "words_written": total_words,
                "target_words": context.outline.total_word_count
            },
            "current_chapter": context.current_chapter + 1 if context.current_chapter < total_chapters else "Complete"
        }

    def export_manuscript(self, format_type: str = "markdown") -> str:
        context = self.context_manager.load_context()
        if not context:
            raise Exception("No active project found")

        if format_type == "markdown":
            output_file = os.path.join(self.project_path, f"{context.outline.title}.md")
            self.context_manager.export_manuscript(output_file)
            return output_file
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def run_story_critique(self) -> Dict[str, Any]:
        context = self.context_manager.load_context()
        if not context:
            raise Exception("No active project found")

        if not context.completed_chapters:
            return {"error": "No completed chapters to critique"}

        # Check recent continuity
        continuity_issues = self.critic.check_continuity(context)

        # If story is complete, run full critique
        if len(context.completed_chapters) == len(context.outline.chapters):
            full_critique = self.critic.critique_full_story(context)
            return {
                "type": "full_story",
                "critique": full_critique,
                "continuity_issues": continuity_issues
            }
        else:
            # Critique the latest chapter
            latest_content = context.completed_chapters[-1]
            latest_index = len(context.completed_chapters) - 1
            chapter_critique = self.critic.critique_chapter(latest_content, latest_index, context)

            return {
                "type": "chapter",
                "chapter_index": latest_index,
                "critique": chapter_critique,
                "continuity_issues": continuity_issues
            }