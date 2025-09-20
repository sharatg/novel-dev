import click
import traceback
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from typing import Dict, Any
import json
import os

from ..core.novel_writer import NovelWriter
from ..core.models import StoryPrompt, StoryType
from ..utils.logger import logger

console = Console()

@click.group()
def cli():
    """AI-powered novel writing assistant using local LLMs."""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--story-type', type=click.Choice(['novel', 'screenplay', 'short_story']),
              default='novel', help='Type of story to write')
@click.option('--genre', help='Story genre')
@click.option('--target-length', type=int, help='Target word count')
def new(project_name: str, story_type: str, genre: str, target_length: int):
    """Start a new writing project."""
    console.print(f"\n[bold blue]Creating new {story_type} project: {project_name}[/bold blue]")

    writer = NovelWriter(project_name)

    if not writer.check_llm_availability():
        console.print("[bold red]Error: Local LLM not available. Please ensure Ollama is running.[/bold red]")
        return

    console.print("\n[yellow]Please provide your story idea:[/yellow]")
    story_content = Prompt.ask("Story prompt")

    style_preferences = Prompt.ask("Style preferences (optional)", default="")

    prompt = StoryPrompt(
        content=story_content,
        story_type=StoryType(story_type),
        genre=genre,
        target_length=target_length,
        style_preferences=style_preferences if style_preferences else None
    )

    try:
        logger.info(f"Starting new project: {project_name}")
        result = writer.start_new_project(prompt)

        console.print("\n[green]✓ Story analyzed successfully![/green]")
        _display_analysis(result)
        _handle_questions(writer, result['questions'])

    except Exception as e:
        logger.error(f"Failed to start new project: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        console.print(f"[dim]Check logs/novel_writer.log for detailed error information[/dim]")

def _display_analysis(result: Dict[str, Any]) -> None:
    analysis = result['analysis']

    console.print("\n[bold]Story Analysis:[/bold]")

    # Strengths
    if analysis.strengths:
        console.print("\n[green]Strengths:[/green]")
        for strength in analysis.strengths:
            console.print(f"  • {strength}")

    # Gaps
    if analysis.gaps:
        console.print("\n[yellow]Areas needing development:[/yellow]")
        for gap in analysis.gaps:
            console.print(f"  • {gap.description} (Severity: {gap.severity}/5)")

    console.print(f"\n[blue]Complexity Score: {analysis.complexity_score}/10[/blue]")

def _handle_questions(writer: NovelWriter, questions) -> None:
    console.print(f"\n[bold]I have {len(questions)} questions to help develop your story:[/bold]")

    answers = {}
    for i, question in enumerate(questions, 1):
        console.print(f"\n[cyan]Question {i}/{len(questions)} ({question.category}):[/cyan]")
        console.print(f"[yellow]{question.question}[/yellow]")

        if question.suggested_answer:
            console.print(f"[dim]Suggested: {question.suggested_answer}[/dim]")

        answer = Prompt.ask("Your answer")
        answers[question.question] = answer

    console.print("\n[blue]Generating story outline...[/blue]")

    try:
        logger.info("Processing question answers and creating outline")
        outline = writer.answer_questions(answers)
        _display_outline(outline)
        _handle_outline_approval(writer, outline)

    except Exception as e:
        logger.error(f"Failed to create outline: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        console.print(f"[bold red]Error creating outline: {str(e)}[/bold red]")
        console.print(f"[dim]Check logs/novel_writer.log for detailed error information[/dim]")

def _display_outline(outline) -> None:
    console.print(f"\n[bold green]Story Outline: {outline.title}[/bold green]")

    panel_content = f"""
[bold]Genre:[/bold] {outline.genre}
[bold]Premise:[/bold] {outline.premise}
[bold]Theme:[/bold] {outline.theme}
[bold]Setting:[/bold] {outline.setting}
[bold]Target Length:[/bold] {outline.total_word_count:,} words
"""

    console.print(Panel(panel_content, title="Story Details"))

    # Characters
    console.print("\n[bold]Main Characters:[/bold]")
    for char in outline.main_characters:
        console.print(f"  • [cyan]{char['name']}[/cyan] ({char['role']}): {char['description']}")

    # Chapters
    console.print(f"\n[bold]Chapter Breakdown ({len(outline.chapters)} chapters):[/bold]")

    table = Table()
    table.add_column("Chapter", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Summary", style="white")
    table.add_column("Words", style="yellow")

    for i, chapter in enumerate(outline.chapters, 1):
        table.add_row(
            str(i),
            chapter.title,
            chapter.summary[:60] + "..." if len(chapter.summary) > 60 else chapter.summary,
            f"{chapter.word_count_target:,}"
        )

    console.print(table)

def _handle_outline_approval(writer: NovelWriter, outline) -> None:
    approved = Confirm.ask("\nDo you approve this outline?")

    if approved:
        console.print("[green]✓ Outline approved! Ready to start writing.[/green]")
        if Confirm.ask("Start writing the first chapter now?"):
            _write_chapter(writer)
    else:
        feedback = Prompt.ask("What changes would you like to make?")
        try:
            revised_outline = writer.approve_outline(False, feedback)
            if revised_outline:
                console.print("\n[blue]Revised outline:[/blue]")
                _display_outline(revised_outline)
                _handle_outline_approval(writer, revised_outline)
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")

@cli.command()
@click.argument('project_name')
def write(project_name: str):
    """Continue writing the current project."""
    writer = NovelWriter(project_name)

    if not writer.check_llm_availability():
        console.print("[bold red]Error: Local LLM not available.[/bold red]")
        return

    _write_chapter(writer)

def _write_chapter(writer: NovelWriter) -> None:
    try:
        status = writer.get_story_status()
        if 'error' in status:
            console.print(f"[bold red]{status['error']}[/bold red]")
            return

        console.print(f"\n[bold]Writing Progress:[/bold]")
        console.print(f"Title: {status['title']}")
        console.print(f"Progress: {status['progress']['chapters_completed']}/{status['progress']['total_chapters']} chapters")
        console.print(f"Words: {status['progress']['words_written']:,}/{status['progress']['target_words']:,}")

        additional_instructions = Prompt.ask("Any specific instructions for this chapter? (optional)", default="")

        console.print(f"\n[blue]Writing chapter {status['current_chapter']}...[/blue]")

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        ) as progress:
            task = progress.add_task("Writing chapter...", total=100)

            result = writer.write_next_chapter(
                additional_instructions if additional_instructions else None
            )

            progress.update(task, completed=100)

        if result['completed']:
            console.print(f"[bold green]{result['message']}[/bold green]")
            return

        console.print(f"\n[green]✓ Chapter {result['chapter_index'] + 1} completed![/green]")
        console.print(f"Title: {result['chapter_title']}")
        console.print(f"Word count: {result['word_count']:,}")

        # Display critique
        critique = result['critique']
        console.print(f"\n[bold]Chapter Critique (Score: {critique.overall_score}/10):[/bold]")

        if critique.strengths:
            console.print("\n[green]Strengths:[/green]")
            for strength in critique.strengths:
                console.print(f"  • {strength}")

        if critique.weaknesses:
            console.print("\n[yellow]Areas for improvement:[/yellow]")
            for weakness in critique.weaknesses:
                console.print(f"  • {weakness}")

        if critique.suggestions:
            console.print("\n[blue]Suggestions:[/blue]")
            for suggestion in critique.suggestions:
                console.print(f"  • {suggestion}")

        # Handle chapter approval
        approved = Confirm.ask("\nApprove this chapter?")

        revisions = None
        if not approved:
            revisions = Prompt.ask("What revisions would you like?")

        writer.finalize_chapter(approved, revisions)

        if approved:
            console.print("[green]✓ Chapter finalized![/green]")
            if Confirm.ask("Continue to next chapter?"):
                _write_chapter(writer)

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

@cli.command()
@click.argument('project_name')
def status(project_name: str):
    """Check the status of a writing project."""
    writer = NovelWriter(project_name)

    try:
        status = writer.get_story_status()
        if 'error' in status:
            console.print(f"[bold red]{status['error']}[/bold red]")
            return

        console.print(f"\n[bold blue]Project Status: {status['title']}[/bold blue]")

        progress = status['progress']

        table = Table()
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Genre", status['genre'])
        table.add_row("Chapters Completed", f"{progress['chapters_completed']}/{progress['total_chapters']}")
        table.add_row("Progress", f"{progress['percentage']:.1f}%")
        table.add_row("Words Written", f"{progress['words_written']:,}")
        table.add_row("Target Words", f"{progress['target_words']:,}")
        table.add_row("Current Chapter", str(status['current_chapter']))

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

@cli.command()
@click.argument('project_name')
@click.option('--format', 'format_type', default='markdown', help='Export format')
def export(project_name: str, format_type: str):
    """Export the completed manuscript."""
    writer = NovelWriter(project_name)

    try:
        output_file = writer.export_manuscript(format_type)
        console.print(f"[green]✓ Manuscript exported to: {output_file}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

@cli.command()
@click.argument('project_name')
def critique(project_name: str):
    """Run a comprehensive critique of the story."""
    writer = NovelWriter(project_name)

    try:
        result = writer.run_story_critique()

        if 'error' in result:
            console.print(f"[bold red]{result['error']}[/bold red]")
            return

        critique = result['critique']

        console.print(f"\n[bold]{result['type'].title()} Critique:[/bold]")
        console.print(f"Overall Score: {critique.overall_score}/10")
        console.print(f"Character Consistency: {critique.character_consistency}/10")
        console.print(f"Plot Coherence: {critique.plot_coherence}/10")

        if critique.strengths:
            console.print("\n[green]Strengths:[/green]")
            for strength in critique.strengths:
                console.print(f"  • {strength}")

        if critique.weaknesses:
            console.print("\n[yellow]Weaknesses:[/yellow]")
            for weakness in critique.weaknesses:
                console.print(f"  • {weakness}")

        if critique.suggestions:
            console.print("\n[blue]Suggestions:[/blue]")
            for suggestion in critique.suggestions:
                console.print(f"  • {suggestion}")

        if result['continuity_issues']:
            console.print("\n[red]Continuity Issues:[/red]")
            for issue in result['continuity_issues']:
                console.print(f"  • {issue}")

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == '__main__':
    cli()