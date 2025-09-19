import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from src.core.models import StoryPrompt, StoryType
from src.core.novel_writer import NovelWriter

class TestBasicFunctionality:

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project_name = "test_novel"

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('src.core.novel_writer.LLMInterface')
    def test_project_creation(self, mock_llm_class):
        mock_llm = Mock()
        mock_llm.is_available.return_value = True
        mock_llm.generate_structured.return_value = {
            "gaps": [],
            "questions": [
                {
                    "question": "What is the protagonist's main goal?",
                    "category": "character",
                    "importance": 5
                }
            ],
            "strengths": ["Interesting premise"],
            "complexity_score": 7
        }
        mock_llm_class.return_value = mock_llm

        writer = NovelWriter(self.project_name, self.temp_dir)

        prompt = StoryPrompt(
            content="A detective story set in future Tokyo",
            story_type=StoryType.NOVEL,
            genre="Science Fiction"
        )

        result = writer.start_new_project(prompt)

        assert "analysis" in result
        assert len(result["questions"]) > 0
        mock_llm.generate_structured.assert_called_once()

    def test_story_prompt_validation(self):
        prompt = StoryPrompt(
            content="A mystery story",
            story_type=StoryType.NOVEL
        )

        assert prompt.content == "A mystery story"
        assert prompt.story_type == StoryType.NOVEL
        assert prompt.genre is None

    def test_project_directory_creation(self):
        writer = NovelWriter(self.project_name, self.temp_dir)
        expected_path = os.path.join(self.temp_dir, self.project_name)

        assert writer.project_path == expected_path
        assert os.path.exists(expected_path)

if __name__ == "__main__":
    pytest.main([__file__])