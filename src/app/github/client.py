"""Async GitHub client tailored for pull request operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class GitHubClientError(Exception):
    """Custom error raised when the GitHub client encounters failures."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(slots=True)
class GitHubClientConfig:
    """Configuration values for the GitHub client."""

    token: str | None
    base_url: str = "https://api.github.com"
    timeout: float = 15.0
    user_agent: str = "CodeReview-Agent/0.1.0"


class GitHubClient:
    """Thin wrapper around httpx.AsyncClient for GitHub REST operations."""

    def __init__(
        self,
        token: str | None,
        base_url: str,
        timeout: float,
        user_agent: str = "CodeReview-Agent/0.1.0",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._config = GitHubClientConfig(
            token=token,
            base_url=base_url,
            timeout=timeout,
            user_agent=user_agent,
        )

        self._default_headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "User-Agent": self._config.user_agent,
        }
        if token:
            self._default_headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.AsyncClient(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            headers=self._default_headers.copy(),
            transport=transport,
        )

    async def __aenter__(self) -> GitHubClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # pragma: no cover - passthrough
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    def _merge_headers(self, overrides: dict[str, str] | None = None) -> dict[str, str]:
        headers = dict(self._default_headers)
        if overrides:
            headers.update(overrides)
        return headers

    def _handle_response(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            message = self._extract_error_message(response)
            raise GitHubClientError(message, status_code=response.status_code) from exc

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f"GitHub API request failed with status {response.status_code}"

        if isinstance(payload, dict) and "message" in payload:
            return str(payload["message"])

        return f"GitHub API request failed with status {response.status_code}"

    async def get_pull_request(self, owner: str, repo: str, number: int) -> dict[str, Any]:
        """Fetch pull request metadata."""

        url = f"/repos/{owner}/{repo}/pulls/{number}"
        try:
            response = await self._client.get(url, headers=self._merge_headers())
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        return response.json()

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        *,
        state: str = "open",
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """List pull requests for a repository."""

        url = f"/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "per_page": str(per_page),
            "page": str(page),
        }

        try:
            response = await self._client.get(
                url,
                headers=self._merge_headers(),
                params=params,
            )
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        data = response.json()
        if not isinstance(data, list):
            raise GitHubClientError("Unexpected response type from GitHub (expected list)")
        return data

    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        number: int,
        *,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Fetch changed files for a pull request."""

        url = f"/repos/{owner}/{repo}/pulls/{number}/files"
        params = {
            "per_page": str(per_page),
            "page": str(page),
        }

        try:
            response = await self._client.get(
                url,
                headers=self._merge_headers(),
                params=params,
            )
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        data = response.json()
        if not isinstance(data, list):
            raise GitHubClientError("Unexpected response type from GitHub (expected list)")
        return data

    async def get_pull_request_commits(
        self,
        owner: str,
        repo: str,
        number: int,
        *,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Fetch commit listings for a pull request."""

        url = f"/repos/{owner}/{repo}/pulls/{number}/commits"
        params = {
            "per_page": str(per_page),
            "page": str(page),
        }

        try:
            response = await self._client.get(
                url,
                headers=self._merge_headers(),
                params=params,
            )
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        data = response.json()
        if not isinstance(data, list):
            raise GitHubClientError("Unexpected response type from GitHub (expected list)")
        return data

    async def get_pull_request_diff(self, owner: str, repo: str, number: int) -> str:
        """Fetch the unified diff for a pull request."""

        url = f"/repos/{owner}/{repo}/pulls/{number}"
        headers = self._merge_headers({"Accept": "application/vnd.github.v3.diff"})

        try:
            response = await self._client.get(url, headers=headers)
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        return response.text

    async def get_pull_request_patch(self, owner: str, repo: str, number: int) -> str:
        """Fetch the patch format for a pull request."""

        url = f"/repos/{owner}/{repo}/pulls/{number}"
        headers = self._merge_headers({"Accept": "application/vnd.github.v3.patch"})

        try:
            response = await self._client.get(url, headers=headers)
        except httpx.RequestError as exc:  # pragma: no cover - network layer failure
            raise GitHubClientError(f"GitHub API request failed: {exc}") from exc

        self._handle_response(response)
        return response.text
