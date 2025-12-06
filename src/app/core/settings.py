"""Application settings and configuration."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "CodeReview Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging
    log_level: str = "info"
    log_format: str = "json"  # json or console

    # GitHub
    github_token: str | None = None
    github_api_url: str = "https://api.github.com"
    github_timeout: float = 15.0
    github_user_agent: str = "CodeReview-Agent/0.1.0"

    # LLM / AI
    # Ollama (local, default)
    llm_base_url: str = "http://ollama:11434"
    llm_model_name: str = "qwen2.5-coder:3b"
    llm_timeout: float = 60.0
    # Cloud LLMs (optional, for comparison)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-sonnet-20240229"

    # Agent Configuration
    max_chunk_size: int = 1000
    reasoning_depth: int = 3
    enable_parallel_agents: bool = True

    # Diff Processing
    max_diff_size_bytes: int = 500000  # 500KB limit
    max_diff_lines: int = 10000  # Maximum lines in diff
    supported_languages: list[str] = [
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        "rust",
        "c",
        "cpp",
        "csharp",
        "ruby",
        "php",
        "swift",
        "kotlin",
    ]  # Languages to review
    supported_extensions: list[str] = [
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".c",
        ".cpp",
        ".cc",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".php",
        ".swift",
        ".kt",
    ]

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
