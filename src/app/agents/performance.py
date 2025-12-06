from __future__ import annotations

import json

from src.app.agents.base import BaseAgent
from src.app.core.logging_config import get_logger
from src.app.models.base import Severity
from src.app.models.code import CodeChunk
from src.app.models.review import ReviewComment

logger = get_logger(__name__)


class PerformanceAgent(BaseAgent):
    """Agent looking for performance issues and inefficiencies."""

    def __init__(self, llm: object) -> None:
        super().__init__(name="performance")
        self._llm = llm

    async def analyze(self, chunk: CodeChunk) -> list[ReviewComment]:
        """Analyze code chunk for performance and efficiency issues."""
        if not chunk.new_lines or len(chunk.new_lines) == 0:
            return []

        prompt = self._build_prompt(chunk)

        try:
            response = await self._llm.generate(prompt, temperature=0.0, max_tokens=800)
            return self._parse_response(response, chunk)
        except Exception as e:
            logger.error("performance_agent_error", error=str(e), file=chunk.file_path)
            return []

    def _build_prompt(self, chunk: CodeChunk) -> str:
        """Build performance analysis prompt."""
        code_context = "\n".join(chunk.new_lines)

        prompt = f"""You are an expert code reviewer specializing in performance optimization. Analyze the following code for efficiency and resource usage.

FILE: {chunk.file_path}
LANGUAGE: {chunk.language.value if chunk.language else "unknown"}
LINES: {chunk.start_line} - {chunk.start_line + len(chunk.new_lines) - 1}

CODE TO REVIEW:
```
{code_context}
```

Focus on these performance issues ONLY (skip if none found):
1. **Algorithm complexity** - O(n²) nested loops when O(n) is possible
2. **Redundant operations** - repeated calculations inside loops
3. **Inefficient data structures** - using lists when sets/dicts would be faster
4. **Memory waste** - creating unnecessary copies of large data structures

BE CONSISTENT: Always return the same issues for the same code. Do not be creative or change your analysis between runs.

For each issue found, return a JSON array with this exact structure:
[
  {{
    "line": <line_number_relative_to_chunk>,
    "severity": "warning",
    "message": "<clear description of the performance issue>",
    "suggestion": "<specific optimization recommendation>"
  }}
]

If no issues found, return: []

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanations, no code blocks."""

        return prompt

    def _parse_response(self, response: str, chunk: CodeChunk) -> list[ReviewComment]:
        """Parse LLM JSON response into ReviewComment objects."""
        if not response or not response.strip():
            return []

        cleaned = response.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(line for line in lines if not line.strip().startswith("```"))

        try:
            issues = json.loads(cleaned.strip())
            if not isinstance(issues, list):
                logger.warning("performance_agent_invalid_format", file=chunk.file_path)
                return []

            comments = []
            for issue in issues:
                try:
                    relative_line = issue.get("line", 0)
                    absolute_line = chunk.start_line + relative_line - 1

                    severity_str = issue.get("severity", "info").lower()
                    severity = (
                        Severity(severity_str)
                        if severity_str in ["warning", "info"]
                        else Severity.INFO
                    )

                    comment = ReviewComment(
                        file_path=chunk.file_path,
                        line_number=absolute_line,
                        severity=severity,
                        category="performance",  # type: ignore[arg-type]
                        message=issue.get("message", "Performance issue detected"),
                        suggestion=issue.get("suggestion"),
                        agent_name=self.name,
                    )
                    comments.append(comment)
                except (ValueError, KeyError) as e:
                    logger.warning("performance_agent_parse_issue", error=str(e), issue=issue)
                    continue

            return comments

        except json.JSONDecodeError as e:
            logger.warning("performance_agent_json_error", error=str(e), response=response[:200])
            return []
