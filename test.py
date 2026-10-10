
import json
import os

import requests
from dotenv import load_dotenv

# Define the YouTube video ID and API endpoint
VIDEO_ID = "ZxM9d1JNWXQ"
URL = "https://www.googleapis.com/youtube/v3/videos"
TIMEOUT = 10  # seconds; prevents the request from waiting indefinitely


def fetch_video(video_id, api_key):
    """Return the video's dictionary, or None if the video ID does not exist.

    Raise RuntimeError with a safe error message (without exposing the API key)
    if the request or response processing fails.
    """
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key,
    }

    try:
        # Send a GET request to the YouTube Data API with a timeout
        response = requests.get(URL, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Network error ({type(error).__name__})"
        ) from None

    # Check whether the API request was successful
    if response.status_code != 200:
        try:
            # Extract the error message returned by the API
            reason = response.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            # Handle responses without a valid or complete error message
            reason = "no details available"

        raise RuntimeError(
            f"API returned status {response.status_code}: {reason}"
        )

    try:
        # Parse the JSON response into a Python dictionary
        data = response.json()
    except ValueError:
        # Handle responses that do not contain valid JSON
        raise RuntimeError("The response is not valid JSON") from None

    # Retrieve the list of videos returned by the API
    items = data.get("items", [])

    # Return the first video if found; otherwise, return None
    return items[0] if items else None


def extract_fields(video):
    """Extract the relevant video fields without failing if any are missing."""
    # Retrieve video metadata, using an empty dictionary if the field is missing
    snippet = video.get("snippet", {})

    # Retrieve the view count, which the API returns as a string
    views = video.get("statistics", {}).get("viewCount")

    # Return only the fields needed for further analysis
    return {
        "title": snippet.get("title"),
        "published_at": snippet.get("publishedAt"),
        "views": int(views) if views is not None else None,
    }


def main():
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve the API key from the environment
    api_key = os.getenv("YOUTUBE_API_KEY")

    # Stop execution if the API key is missing
    if not api_key:
        raise SystemExit(
            "YOUTUBE_API_KEY not found. Check your .env file."
        )

    try:
        # Fetch the video data from the YouTube Data API
        video = fetch_video(VIDEO_ID, api_key)
    except RuntimeError as error:
        # Display the error and exit with a non-zero status code
        raise SystemExit(f"Error: {error}")

    # Stop execution if no video matches the specified ID
    if video is None:
        raise SystemExit("No video found for the specified ID.")

    # Extract the relevant fields and print them as formatted JSON
    print(
        json.dumps(
            extract_fields(video),
            indent=2,
            ensure_ascii=False,
        )
    )


# Run main() only when this script is executed directly
if __name__ == "__main__":
    main()
