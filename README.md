# 📚 Novel Writer AI

> An intelligent AI writing assistant that helps you craft complete novels, screenplays, and short stories using local LLMs

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

**Novel Writer AI** is a sophisticated writing assistant that uses local Large Language Models to help you create coherent, full-length narratives. Unlike simple text generators, this system maintains story context, tracks character development, and provides intelligent critique throughout the writing process.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Story Analysis** | Analyzes your initial story prompt and identifies gaps |
| ❓ **Interactive Questioning** | Asks clarifying questions to develop your story |
| 📋 **Intelligent Outlining** | Creates detailed, structured outlines |
| ✍️ **Iterative Writing** | Writes chapters while maintaining context and continuity |
| 🎯 **Self-Critique** | Reviews and critiques content as it's written |
| 🧠 **Context Management** | Maintains character arcs, plot threads, and world-building |
| 🏠 **Local LLM** | Works completely offline using Ollama |
| 📖 **Multiple Formats** | Supports novels, screenplays, and short stories |

## 🎬 Demo

```
$ python -m src.main new "space-opera" --story-type novel --genre "science fiction"

📚 Creating new novel project: space-opera

🔍 Story analyzed successfully!
   Strengths: • Interesting premise • Strong genre foundation
   Complexity Score: 8/10

❓ I have 7 questions to help develop your story:
   Question 1/7 (character): What drives your protagonist's main conflict?
   ...

📋 Generating story outline...
   ✅ 18 chapters planned • 75,000 target words
   ✅ 4 main characters developed • Plot threads established

✍️ Ready to start writing!
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **[Ollama](https://ollama.ai/)** for local LLM inference
- **8GB+ RAM** recommended for optimal performance

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sharatg/novel-writer-ai.git
   cd novel-writer-ai
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai/ for OS-specific instructions)

   # Pull a compatible model
   ollama pull llama3.1:8b  # or llama3.1:70b for better quality

   # Start Ollama service
   ollama serve
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings (optional)
   ```

5. **Test installation**
   ```bash
   python -m src.main --help
   ```

## 📖 Usage Guide

### 🆕 Start a New Project

```bash
# Create a new novel
python -m src.main new "my-fantasy-epic" --story-type novel --genre fantasy

# Create a screenplay
python -m src.main new "sci-fi-thriller" --story-type screenplay --genre "science fiction"

# Create a short story
python -m src.main new "mystery-tale" --story-type short_story --target-length 5000
```

**The system will then:**
1. 🔍 Analyze your story prompt for gaps and strengths
2. ❓ Ask 5-10 targeted questions to develop your story
3. 📋 Generate a detailed chapter-by-chapter outline
4. ✅ Request your approval before proceeding

### ✍️ Continue Writing

```bash
python -m src.main write "my-fantasy-epic"
```

**Each writing session:**
1. 📝 Writes the next chapter (2,000-4,000 words)
2. 🎯 Provides automated critique and suggestions
3. 🔄 Allows you to approve or request revisions
4. 📊 Updates character arcs and plot threads

### 📊 Project Management

```bash
# Check writing progress
python -m src.main status "my-fantasy-epic"

# Export finished manuscript
python -m src.main export "my-fantasy-epic" --format markdown

# Get comprehensive story critique
python -m src.main critique "my-fantasy-epic"
```

## 🔧 How It Works

<details>
<summary><strong>🔍 Phase 1: Story Analysis</strong></summary>

- Analyzes your initial prompt for narrative strengths and gaps
- Identifies missing story elements (characters, plot, setting, themes)
- Generates targeted questions to fill identified gaps
- Provides complexity scoring and genre analysis

</details>

<details>
<summary><strong>📋 Phase 2: Outline Creation</strong></summary>

- Uses your answers to create a detailed story outline
- Breaks the story into chapters with summaries and key events
- Establishes character arcs and plot threads
- Allows iterative revision based on your feedback

</details>

<details>
<summary><strong>✍️ Phase 3: Iterative Writing</strong></summary>

- Writes chapters one at a time with full context awareness
- Maintains character voice and story consistency
- Tracks character development and plot progression
- Updates world-building notes and plot threads automatically

</details>

<details>
<summary><strong>🎯 Phase 4: Intelligent Critique</strong></summary>

- Reviews each chapter for quality, pacing, and consistency
- Checks continuity with previous chapters
- Identifies character development and plot coherence issues
- Provides specific, actionable suggestions for improvement

</details>

<details>
<summary><strong>🧠 Phase 5: Context Management</strong></summary>

- Maintains character arcs and relationships throughout the story
- Tracks multiple plot threads and their resolution
- Preserves world-building details and consistency
- Ensures overall narrative coherence and thematic development

</details>

## 🏗️ Project Architecture

```
novel-writer-ai/
├── src/
│   ├── core/                    # 🧠 Core Engine
│   │   ├── models.py           # Data models & schemas
│   │   ├── llm_interface.py    # Ollama integration
│   │   ├── context_manager.py  # Story state management
│   │   └── novel_writer.py     # Main orchestrator
│   ├── agents/                 # 🤖 Specialized AI Agents
│   │   ├── story_analyzer.py   # Story gap analysis
│   │   ├── outline_creator.py  # Chapter planning
│   │   ├── writing_engine.py   # Content generation
│   │   └── story_critic.py     # Quality assessment
│   └── interfaces/             # 💻 User Interface
│       └── cli.py             # Rich command-line interface
├── projects/                   # 📁 Your Writing Projects
├── tests/                     # 🧪 Test Suite
└── data/                      # 📊 Application Data
```

### 🎛️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server endpoint |
| `OLLAMA_MODEL` | `llama3.1:8b` | LLM model for generation |
| `MAX_CONTEXT_LENGTH` | `8192` | Maximum tokens per request |
| `WRITING_CHUNK_SIZE` | `1000` | Target words per writing session |
| `CRITIQUE_FREQUENCY` | `3` | Chapters between full critiques |

## 📚 Supported Story Types

| Type | Structure | Length | Best For |
|------|-----------|--------|----------|
| 📖 **Novel** | 15-25 chapters | 50,000-150,000 words | Complex narratives, character development |
| 🎬 **Screenplay** | Acts & scenes | 90-120 pages | Visual storytelling, dialogue-driven plots |
| 📝 **Short Story** | 3-7 sections | 2,000-10,000 words | Focused concepts, experimental narratives |

## 💡 Tips for Best Results

### 🎯 Writing Quality
- **Rich initial prompts**: Include character motivations, setting details, and thematic elements
- **Thoughtful questioning**: Answer analysis questions comprehensively
- **Outline review**: Carefully examine and refine outlines before writing
- **Active feedback**: Provide specific revision requests when needed

### 🚀 Performance Optimization
- **Model selection**: Use `llama3.1:70b` for higher quality (requires more RAM)
- **Context length**: Adjust `MAX_CONTEXT_LENGTH` based on your hardware
- **Regular exports**: Backup your work frequently
- **Project management**: Archive completed projects to save memory

## 🔧 Troubleshooting

<details>
<summary><strong>🚨 "Local LLM not available"</strong></summary>

```bash
# Check if Ollama is running
ollama serve

# Verify model installation
ollama list

# Test model directly
ollama run llama3.1:8b "Hello, world!"

# Check .env configuration
cat .env
```

</details>

<details>
<summary><strong>📉 Poor quality output</strong></summary>

- **Upgrade model**: `ollama pull llama3.1:70b` (requires 40GB+ RAM)
- **Improve prompts**: Provide more detailed story context
- **Adjust settings**: Lower temperature for more focused output
- **Review critique**: Use the built-in critique system actively

</details>

<details>
<summary><strong>💾 Memory/performance issues</strong></summary>

- **Reduce context**: Set `MAX_CONTEXT_LENGTH=4096` in `.env`
- **Smaller model**: Use `llama3.1:8b` instead of larger variants
- **Clean projects**: Remove old project directories
- **Close applications**: Free up system memory before long writing sessions

</details>

## 🤝 Contributing

We welcome contributions! Here's how you can help:

- 🐛 **Bug reports**: Create an issue with details and reproduction steps
- 💡 **Feature requests**: Propose new functionality or improvements
- 🔧 **Pull requests**: Submit code improvements or fixes
- 📖 **Documentation**: Improve guides, examples, or code comments
- 🎨 **UI/UX**: Suggest interface improvements or new output formats

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/yourusername/novel-writer-ai.git
cd novel-writer-ai

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
python -m pytest tests/ -v

# Format code
black src/ tests/
```

## 📄 License

**MIT License** - Feel free to use, modify, and distribute this software.

See [LICENSE](LICENSE) file for full details.

---

## 🌟 Star History

If this project helped you write your story, please consider giving it a star! ⭐
