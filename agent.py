import json
import logging
import os
from datetime import datetime
from typing import Annotated, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logfire
import requests
from pydantic import Field, BaseModel
from pydantic_ai import Agent, RunContext, BinaryContent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from config import settings
from context import QUERY_SEARCH_SYNTAX_DOCS
from utils import init_logging

init_logging()
logger = logging.getLogger(__name__)

logfire.configure(
    send_to_logfire="if-token-present",
    environment="development",
    service_name="rapid-assistant",
)
logfire.instrument_openai()
logfire.instrument_requests(capture_all=True)
logfire.instrument_pydantic()

main_agent = Agent(
    OpenAIModel(
        settings.openai_model,
        provider=OpenAIProvider(api_key=settings.openai_api_key),
    ),
    model_settings=ModelSettings(temperature=settings.temperature),
    system_prompt=(
        "You are an autonomous AI agent specialized in searching and downloading content from the "
        "internet. You can search for any type of content using SearXNG search engine REST API"
        " and download various types of files including images, web pages, and documents. "
        "You store all downloaded content and metadata in a local directory."
    ),
    instrument=True,
)


analyze_agent = Agent(
    OpenAIModel(
        settings.openai_model,
        provider=OpenAIProvider(api_key=settings.openai_api_key),
    ),
    model_settings=ModelSettings(temperature=settings.temperature),
    system_prompt=(
        "You are an autonomous AI agent specialized in describing "
        "and summarizing provided content."
    ),
    instrument=True,
)


class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    img_src: str | None


@main_agent.tool
async def analyze(
    ctx: RunContext[None],
    file: Annotated[
        str, Field(description="File name to be analyzed and described")
    ],
    query: Annotated[
        str, Field(description="Query to analyze the content of the file")
    ],
) -> str:
    """
    Analyze the content of a file and return a description based on the query.
    """
    with open(settings.storage_dir / file, "rb") as f:
        content = f.read()

    with open(settings.storage_dir / f"{file}.meta.json", "rb") as f:
        metadata = json.load(f)

    if metadata["content_type"] == "image/jpeg":
        response = await analyze_agent.run(
            [
                query,
                BinaryContent(
                    data=content, media_type=metadata["content_type"]
                ),
            ]
        )
    elif metadata["content_type"] == "text/html":
        result = BeautifulSoup(content.decode("utf-8"), "html.parser")
        response = await analyze_agent.run([query, result.text])
    else:
        response = await analyze_agent.run([query, content.decode("utf-8")])

    return response.output


@main_agent.tool
async def search(
    ctx: RunContext[None],
    searxng_query: Annotated[str, Field(description=QUERY_SEARCH_SYNTAX_DOCS)],
    num_results: Annotated[
        int, Field(default=5, ge=1, description="Number of results to return")
    ],
) -> list[SearchResult]:
    """
    Search for content using SearXNG search engine. Use special queries if needed.

    Returns:
        List of search results containing title, url, img_src
    """
    params = {"q": searxng_query, "format": "json", "pageno": 1}
    logger.debug(f"Making search request with params: {params}")

    response = requests.get(
        f"{settings.searxng_url}/search",
        params=params,
        timeout=settings.timeout,
    )
    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])
    logger.info(f"Search completed successfully. Found {len(results)} results")
    return [SearchResult.model_validate(r) for r in results[:num_results]]


@main_agent.tool(retries=2)
async def download(
    ctx: RunContext[None],
    url: Annotated[
        str, Field(description="Content URL to download or IMG source URL")
    ],
) -> dict[str, Any]:
    """
    Download content from a URL and store it with metadata.
    Return metadata with file name for further analysis.
    """
    try:
        response = requests.get(url, timeout=settings.timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return

    content_type = response.headers.get("content-type", "").split(";")[0]
    filename = os.path.basename(urlparse(url).path)
    type_extensions = {"text/html": ".html", "text/plain": ".txt"}
    if content_type.startswith("image/"):
        ext = f".{content_type.split('/')[1]}"
        if not filename.endswith(ext):
            filename += ext
    elif content_type in type_extensions:
        ext = type_extensions[content_type]
        if not filename.endswith(ext):
            filename += ext

    filepath = settings.storage_dir / filename
    logger.info(f"Saving content to: {filepath}")
    with open(filepath, "wb") as f:
        f.write(response.content)

    metadata = {
        "url": url,
        "filename": filename,
        "content_type": content_type,
        "size": len(response.content),
        "downloaded_at": datetime.now().isoformat(),
        "headers": dict(response.headers),
    }
    metadata_path = f"{filepath}.meta.json"
    logger.debug(f"Saving metadata to: {metadata_path}")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


if __name__ == "__main__":
    main_agent.run_sync(
        "Check on guardians press site for the top stories today, "
        "summarize them into few bullet points."
    )
