from __future__ import annotations

import json

from src.app.agents.base import BaseAgent
from src.app.core.logging_config import get_logger
from src.app.models.base import Severity
from src.app.models.code import CodeChunk
from src.app.models.review import ReviewComment

logger = get_logger(__name__)


class LogicAgent(BaseAgent):
    """Agent focused on logical flaws and edge cases."""

    def __init__(self, llm: object) -> None:
        super().__init__(name="logic")
        self._llm = llm

    async def analyze(self, chunk: CodeChunk) -> list[ReviewComment]:
        """Analyze code chunk for logical errors and edge cases.

        Uses LLM to identify:
        - Off-by-one errors
        - Null pointer / None checks
        - Edge case handling
        - Control flow issues
        - Logic bugs
        """
        if not chunk.new_lines or len(chunk.new_lines) == 0:
            return []

        prompt = self._build_prompt(chunk)

        try:
            response = await self._llm.generate(prompt, temperature=0.0, max_tokens=800)
            return self._parse_response(response, chunk)
        except Exception as e:
            logger.error("logic_agent_error", error=str(e), file=chunk.file_path)
            return []

    def _build_prompt(self, chunk: CodeChunk) -> str:
        """Build comprehensive logic analysis prompt."""
        code_context = "\n".join(chunk.new_lines)

        prompt = f"""You are an expert code reviewer specializing in logic analysis. Analyze the following code for logical flaws, edge cases, and potential bugs.

FILE: {chunk.file_path}
LANGUAGE: {chunk.language.value if chunk.language else "unknown"}
LINES: {chunk.start_line} - {chunk.start_line + len(chunk.new_lines) - 1}

CODE TO REVIEW:
```
{code_context}
```

Focus on these critical logic issues ONLY (skip if none found):
1. **Division by zero** - calculations that could divide by 0
2. **Null/None checks** - missing validation that could cause crashes
3. **Edge cases** - empty inputs, boundary conditions (e.g., empty lists, zero values)
4. **Off-by-one errors** in loops and array indexing
5. **Unreachable code** or infinite loops

BE CONSISTENT: Always return the same issues for the same code. Do not be creative or change your analysis between runs.

For each issue found, return a JSON array with this exact structure:
[
  {{
    "line": <line_number_relative_to_chunk>,
    "severity": "critical",
    "message": "<clear, specific description of the issue>",
    "suggestion": "<concrete fix or recommendation>"
  }}
]

If no issues found, return: []

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanations, no code blocks."""

        return prompt

    def _parse_response(self, response: str, chunk: CodeChunk) -> list[ReviewComment]:
        """Parse LLM JSON response into ReviewComment objects."""
        if not response or not response.strip():
            return []

        # Clean up response - remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # Remove markdown code fences
            lines = cleaned.split("\n")
            cleaned = "\n".join(line for line in lines if not line.strip().startswith("```"))

        try:
            issues = json.loads(cleaned.strip())
            if not isinstance(issues, list):
                logger.warning("logic_agent_invalid_format", file=chunk.file_path)
                return []

            comments = []
            for issue in issues:
                try:
                    # Convert relative line to absolute
                    relative_line = issue.get("line", 0)
                    absolute_line = chunk.start_line + relative_line - 1

                    severity_str = issue.get("severity", "warning").lower()
                    severity = (
                        Severity(severity_str)
                        if severity_str in ["critical", "warning", "info"]
                        else Severity.WARNING
                    )

                    comment = ReviewComment(
                        file_path=chunk.file_path,
                        line_number=absolute_line,
                        severity=severity,
                        category="logic",  # type: ignore[arg-type]
                        message=issue.get("message", "Logic issue detected"),
                        suggestion=issue.get("suggestion"),
                        agent_name=self.name,
                    )
                    comments.append(comment)
                except (ValueError, KeyError) as e:
                    logger.warning("logic_agent_parse_issue", error=str(e), issue=issue)
                    continue

            return comments

        except json.JSONDecodeError as e:
            logger.warning("logic_agent_json_error", error=str(e), response=response[:200])
            return []
