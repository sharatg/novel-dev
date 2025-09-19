from typing import Optional
import os
from datetime import datetime
from ..core.models import StoryContext, Chapter, WritingSession
from ..core.llm_interface import LLMInterface
from ..core.context_manager import ContextManager

class WritingEngine:
    def __init__(self, llm: LLMInterface, context_manager: ContextManager):
        self.llm = llm
        self.context_manager = context_manager

    def write_chapter(self, chapter_index: int, context: StoryContext,
                     additional_instructions: Optional[str] = None) -> str:
        if chapter_index >= len(context.outline.chapters):
            raise ValueError("Chapter index out of range")

        chapter = context.outline.chapters[chapter_index]

        system_prompt = """You are a professional novelist. Write engaging, well-crafted prose
that maintains consistency with the established story, characters, and world.

Key guidelines:
- Maintain character voice and personality
- Follow the established writing style
- Ensure plot coherence with previous chapters
- Write vivid, immersive scenes
- Show don't tell
- Use appropriate pacing for the genre
- Include dialogue that advances plot and character development"""

        writing_prompt = self._build_writing_prompt(chapter, context, additional_instructions)

        content = self.llm.generate(
            writing_prompt,
            system_prompt,
            temperature=0.8,
            max_tokens=int(chapter.word_count_target * 1.5)
        )

        session = WritingSession(
            chapter_index=chapter_index,
            content_written=content,
            word_count=len(content.split()),
            timestamp=datetime.now().isoformat()
        )
        self.context_manager.save_session(session)

        return content

    def continue_chapter(self, chapter_index: int, existing_content: str,
                        context: StoryContext, continuation_note: str = "") -> str:
        chapter = context.outline.chapters[chapter_index]

        system_prompt = """Continue writing this chapter seamlessly. Maintain the same voice,
style, and pacing. Pick up exactly where the previous content left off."""

        continuation_prompt = f"""
Continue writing this chapter:

Chapter: {chapter.title}
Chapter Summary: {chapter.summary}
Key Events Still Needed: {', '.join(chapter.key_events)}

Existing Content:
{existing_content}

{continuation_note}

Continue the chapter, picking up seamlessly from where it left off.
Target another {chapter.word_count_target - len(existing_content.split())} words approximately.
"""

        continuation = self.llm.generate(
            continuation_prompt,
            system_prompt,
            temperature=0.8
        )

        return existing_content + "\n\n" + continuation

    def _build_writing_prompt(self, chapter: Chapter, context: StoryContext,
                            additional_instructions: Optional[str] = None) -> str:
        prompt_parts = [
            f"Write Chapter {context.current_chapter + 1}: {chapter.title}",
            f"\nChapter Summary: {chapter.summary}",
            f"\nKey Events to Include: {', '.join(chapter.key_events)}",
            f"\nCharacters Involved: {', '.join(chapter.characters_involved)}",
            f"\nTarget Word Count: {chapter.word_count_target}",
            f"\n\nStory Context:",
            f"Title: {context.outline.title}",
            f"Genre: {context.outline.genre}",
            f"Theme: {context.outline.theme}",
            f"Setting: {context.outline.setting}",
        ]

        if context.style_notes:
            prompt_parts.append(f"\nStyle Notes: {context.style_notes}")

        prompt_parts.append(f"\nMain Characters:")
        for char in context.outline.main_characters:
            arc_status = context.character_arcs.get(char["name"], "Beginning of arc")
            prompt_parts.append(f"- {char['name']} ({char['role']}): {char['description']}")
            prompt_parts.append(f"  Current Arc Status: {arc_status}")

        if context.plot_threads:
            prompt_parts.append(f"\nActive Plot Threads:")
            for thread, status in context.plot_threads.items():
                prompt_parts.append(f"- {thread}: {status}")

        if context.world_building_notes:
            prompt_parts.append(f"\nWorld Building Notes:")
            for key, note in context.world_building_notes.items():
                prompt_parts.append(f"- {key}: {note}")

        recent_content = self.context_manager.get_recent_content(2)
        if recent_content:
            prompt_parts.append(f"\nRecent Chapter Content (for continuity):")
            prompt_parts.append(recent_content[:2000])

        if additional_instructions:
            prompt_parts.append(f"\nAdditional Instructions: {additional_instructions}")

        prompt_parts.append(f"\nNow write the full chapter content:")

        return "\n".join(prompt_parts)

    def finalize_chapter(self, chapter_index: int, content: str, context: StoryContext) -> None:
        context.completed_chapters.append(content)
        context.current_chapter = chapter_index + 1

        self._update_character_arcs(chapter_index, content, context)
        self._update_plot_threads(chapter_index, content, context)

        self.context_manager.save_context(context)

    def _update_character_arcs(self, chapter_index: int, content: str, context: StoryContext) -> None:
        chapter = context.outline.chapters[chapter_index]

        system_prompt = """Analyze this chapter content and update character arcs based on
their development, decisions, and growth shown in the chapter."""

        for char_name in chapter.characters_involved:
            if char_name in [c["name"] for c in context.outline.main_characters]:
                prompt = f"""
Character: {char_name}
Previous Arc Status: {context.character_arcs.get(char_name, 'Beginning')}
Chapter Content: {content[:1500]}

Provide a brief update on this character's arc development in this chapter.
"""
                arc_update = self.llm.generate(prompt, system_prompt, temperature=0.5)
                context.character_arcs[char_name] = arc_update

    def _update_plot_threads(self, chapter_index: int, content: str, context: StoryContext) -> None:
        system_prompt = """Analyze this chapter and update the status of relevant plot threads
based on how they advanced or resolved."""

        prompt = f"""
Chapter {chapter_index + 1} Content: {content[:1500]}
Current Plot Threads: {context.plot_threads}

Update the status of any plot threads that were advanced or affected in this chapter.
Provide brief status updates only for threads that changed.
"""

        if context.plot_threads:
            updates = self.llm.generate(prompt, system_prompt, temperature=0.5)
            # Parse and update plot threads (simplified - could be made more sophisticated)
            for thread_name in context.plot_threads.keys():
                if thread_name.lower() in updates.lower():
                    context.plot_threads[thread_name] = f"Updated after Chapter {chapter_index + 1}"