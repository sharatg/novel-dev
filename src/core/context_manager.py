from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime
from ..core.models import StoryContext, StoryOutline, WritingSession

class ContextManager:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.context_file = os.path.join(project_dir, "story_context.json")
        self.sessions_file = os.path.join(project_dir, "writing_sessions.json")
        os.makedirs(project_dir, exist_ok=True)

    def save_context(self, context: StoryContext) -> None:
        with open(self.context_file, 'w') as f:
            json.dump(context.model_dump(), f, indent=2)

    def load_context(self) -> Optional[StoryContext]:
        if not os.path.exists(self.context_file):
            return None
        with open(self.context_file, 'r') as f:
            data = json.load(f)
            return StoryContext(**data)

    def save_session(self, session: WritingSession) -> None:
        sessions = self.load_sessions()
        sessions.append(session.model_dump())
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)

    def load_sessions(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.sessions_file):
            return []
        with open(self.sessions_file, 'r') as f:
            return json.load(f)

    def update_character_arc(self, character_name: str, arc_update: str) -> None:
        context = self.load_context()
        if context:
            context.character_arcs[character_name] = arc_update
            self.save_context(context)

    def update_plot_thread(self, thread_name: str, thread_update: str) -> None:
        context = self.load_context()
        if context:
            context.plot_threads[thread_name] = thread_update
            self.save_context(context)

    def add_world_building_note(self, key: str, note: str) -> None:
        context = self.load_context()
        if context:
            context.world_building_notes[key] = note
            self.save_context(context)

    def get_recent_content(self, num_chapters: int = 3) -> str:
        context = self.load_context()
        if not context:
            return ""

        start_idx = max(0, context.current_chapter - num_chapters)
        recent_chapters = context.completed_chapters[start_idx:context.current_chapter]
        return "\n\n".join(recent_chapters)

    def get_character_summary(self) -> str:
        context = self.load_context()
        if not context:
            return ""

        summary = []
        for char in context.outline.main_characters:
            arc = context.character_arcs.get(char["name"], "No arc updates")
            summary.append(f"{char['name']} ({char['role']}): {char['description']}\nCurrent Arc: {arc}")

        return "\n\n".join(summary)

    def get_plot_summary(self) -> str:
        context = self.load_context()
        if not context:
            return ""

        summary = [f"Theme: {context.outline.theme}"]
        summary.append(f"Setting: {context.outline.setting}")

        for thread_name, thread_status in context.plot_threads.items():
            summary.append(f"{thread_name}: {thread_status}")

        return "\n".join(summary)

    def export_manuscript(self, output_file: str) -> None:
        context = self.load_context()
        if not context:
            return

        with open(output_file, 'w') as f:
            f.write(f"# {context.outline.title}\n\n")
            f.write(f"**Genre:** {context.outline.genre}\n")
            f.write(f"**Premise:** {context.outline.premise}\n")
            f.write(f"**Theme:** {context.outline.theme}\n\n")
            f.write("---\n\n")

            for i, chapter_content in enumerate(context.completed_chapters):
                chapter = context.outline.chapters[i]
                f.write(f"## Chapter {i+1}: {chapter.title}\n\n")
                f.write(chapter_content)
                f.write("\n\n---\n\n")