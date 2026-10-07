import unittest
from unittest.mock import AsyncMock, patch

from what_now import agent
from what_now.web_context import (
    _page_excerpt,
    add_web_references,
    extract_progress_context,
)


TASK_NOTES = (
    "Solve at least 2-5 coding questions daily, is following "
    "https://takeuforward.org/prep-hub/strivers-a2z-dsa-sheet?page=sheet "
    "striver's a2z sheet, currently covered till time & space complexity section, "
    "need to proceed with stl c++ or collections java or pstl python"
)

TASK_TITLE = (
    "Preparation for DSA for Career "
    "(Placements, Internships & Technical Interviews)"
)


def response(action: str, why: str, first_step: str = "Review the task notes.") -> dict:
    return {
        "task_title": TASK_TITLE,
        "action": action,
        "why": why,
        "first_step": first_step,
        "timebox_minutes": 20,
        "fallback": "Compare one beginner exercise from each track.",
    }


class ProgressExtractionTests(unittest.TestCase):
    def test_completed_milestone_is_separate_from_next_options(self) -> None:
        self.assertEqual(
            extract_progress_context(TASK_NOTES),
            {
                "completed_milestones": ["time & space complexity section"],
                "next_step_options": [
                    "stl c++",
                    "collections java",
                    "pstl python",
                ],
                "next_step_requires_choice": True,
            },
        )

    def test_page_excerpt_prioritizes_next_options_not_completed_section(self) -> None:
        html = b"""<html><body>
        <h2>Time and Space Complexity</h2><p>Review Big O analysis.</p>
        <h2>STL C++</h2><p>Practice vectors and iterators.</p>
        <h2>Collections Java</h2><p>Practice lists and maps.</p>
        <h2>PSTL Python</h2><p>Practice Python collections.</p>
        </body></html>"""

        result = _page_excerpt(
            "https://example.org/roadmap",
            "text/html",
            html,
            TASK_NOTES,
        )

        self.assertNotIn("Review Big O analysis", result["text"])
        self.assertIn("STL C++", result["text"])
        self.assertIn("Collections Java", result["text"])
        self.assertIn("PSTL Python", result["text"])


class ProgressPromptContextTests(unittest.IsolatedAsyncioTestCase):
    async def test_checkin_context_marks_milestone_and_options_separately(self) -> None:
        context = {
            "tasks": [
                {
                    "title": TASK_TITLE,
                    "notes": TASK_NOTES,
                    "progress": 1,
                }
            ]
        }
        with patch(
            "what_now.web_context._fetch_page",
            new_callable=AsyncMock,
            return_value={
                "url": "https://example.org/roadmap",
                "title": "Roadmap",
                "text": "STL, Collections and PSTL sections.",
            },
        ):
            enriched = await add_web_references(context)

        task = enriched["tasks"][0]
        self.assertEqual(
            task["progress_context"]["completed_milestones"],
            ["time & space complexity section"],
        )
        self.assertEqual(
            task["progress_context"]["next_step_options"],
            ["stl c++", "collections java", "pstl python"],
        )
        self.assertNotIn("progress_context", context["tasks"][0])


class NextActionProgressTests(unittest.IsolatedAsyncioTestCase):
    def context(self) -> dict:
        return {
            "available_minutes": 45,
            "tasks": [{"title": TASK_TITLE, "notes": TASK_NOTES, "progress": 1}],
            "recent_suggestions": [],
        }

    async def test_completed_status_only_action_is_revised(self) -> None:
        context = self.context()
        unhelpful = response(
            "Review the time and space complexity section.",
            "The notes state you are currently covered until time and space complexity.",
        )
        forward = response(
            "Compare STL C++ and Collections Java against the languages used in "
            "your target interviews.",
            "Your notes mark complexity as covered and list STL C++, Collections Java, "
            "and PSTL Python as next tracks, so use this step to choose one.",
            "Write down the language used most often in your target interview roles.",
        )
        with (
            patch.object(
                agent,
                "add_web_references",
                new_callable=AsyncMock,
                return_value=context,
            ),
            patch.object(
                agent,
                "_request_action",
                new_callable=AsyncMock,
                side_effect=[unhelpful, forward],
            ) as request_action,
        ):
            result = await agent.get_next_action(context)

        self.assertIn("Compare STL C++", result["action"])
        self.assertEqual(result["timebox_minutes"], 45)
        self.assertEqual(request_action.await_count, 2)
        self.assertIn(
            "Do not describe the completed milestone as the recommendation",
            request_action.await_args_list[1].args[0],
        )

    async def test_repeated_status_paraphrase_gets_grounded_choice_fallback(self) -> None:
        context = self.context()
        unhelpful = response(
            "Review the time and space complexity section.",
            "The notes state you are currently covered until time and space complexity.",
        )
        with (
            patch.object(
                agent,
                "add_web_references",
                new_callable=AsyncMock,
                return_value=context,
            ),
            patch.object(
                agent,
                "_request_action",
                new_callable=AsyncMock,
                return_value=unhelpful,
            ),
        ):
            result = await agent.get_next_action(context)

        self.assertIn("Choose between stl c++, collections java or pstl python", result["action"])
        self.assertIn("mark time & space complexity section as covered", result["why"])
        self.assertEqual(result["timebox_minutes"], 45)


if __name__ == "__main__":
    unittest.main()
