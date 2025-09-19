from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class StoryType(str, Enum):
    NOVEL = "novel"
    SCREENPLAY = "screenplay"
    SHORT_STORY = "short_story"

class StoryPrompt(BaseModel):
    content: str
    story_type: StoryType = StoryType.NOVEL
    target_length: Optional[int] = None
    genre: Optional[str] = None
    style_preferences: Optional[str] = None

class StoryQuestion(BaseModel):
    question: str
    category: str
    importance: int = Field(ge=1, le=5)
    suggested_answer: Optional[str] = None

class StoryGap(BaseModel):
    description: str
    category: str
    severity: int = Field(ge=1, le=5)
    related_questions: List[str] = []

class StoryAnalysis(BaseModel):
    gaps: List[StoryGap]
    questions: List[StoryQuestion]
    strengths: List[str]
    genre_analysis: Optional[str] = None
    complexity_score: int = Field(ge=1, le=10)

class Chapter(BaseModel):
    title: str
    summary: str
    key_events: List[str]
    characters_involved: List[str]
    word_count_target: int
    content: Optional[str] = None

class StoryOutline(BaseModel):
    title: str
    premise: str
    theme: str
    main_characters: List[Dict[str, Any]]
    setting: str
    chapters: List[Chapter]
    total_word_count: int
    genre: str

class WritingSession(BaseModel):
    chapter_index: int
    content_written: str
    word_count: int
    timestamp: str
    critique_notes: Optional[str] = None

class StoryContext(BaseModel):
    outline: StoryOutline
    completed_chapters: List[str] = []
    current_chapter: int = 0
    character_arcs: Dict[str, str] = {}
    plot_threads: Dict[str, str] = {}
    world_building_notes: Dict[str, str] = {}
    style_notes: str = ""

class CritiqueResult(BaseModel):
    overall_score: int = Field(ge=1, le=10)
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    continuity_issues: List[str] = []
    character_consistency: int = Field(ge=1, le=10)
    plot_coherence: int = Field(ge=1, le=10)