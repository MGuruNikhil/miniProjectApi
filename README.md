# Basic Backend for Mini Project

This project provides a backend service to summarize YouTube video transcripts using Flask and the Hugging Face Transformers library.

## Setting up a Virtual Environment

Before installing the project dependencies, it is recommended to create and activate a virtual environment. This helps to isolate the project's dependencies from the global Python environment.

### Linux and macOS

```sh
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Windows

```sh
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

Once the virtual environment is activated, you can proceed with installing the project dependencies using the command mentioned earlier.

## Requirements

The project dependencies are listed in the `requirements.txt` file. You can install them using:

```sh
pip install -r requirements.txt
```


## Project Structure

```
__pycache__/
.gitignore
app.py
README.md
requirements.txt
```

## Usage

1. ## Run the Flask Application:
    ```sh
    python app.py
    ```

2. ## API Endpoint

    The application provides a single API endpoint to get the summary of a YouTube video transcript.

    - **GET /summary**

    Query Parameters:
    - `url`: The URL of the YouTube video.

    Example Request:

    ```sh
    curl "http://127.0.0.1:5000/summary?url=https://www.youtube.com/watch?v=example"
    ```

## Code Overview

### `app.py`

- **Imports:**

    ```python
    from flask import Flask, request, jsonify
    from youtube_transcript_api import YouTubeTranscriptApi
    from transformers import pipeline
    ```

- **Flask Application Setup:**

    ```python
    app = Flask(__name__)
    ```

- **API Endpoint:**

    ```python
    @app.get('/summary')
    def summary_api():
        url = request.args.get('url', '')
        video_id = url.split('=')[1]
        summary = get_summary(get_transcript(video_id))
        print(summary)
        return jsonify(summary), 200
    ```

- **Helper Functions:**

    ```python
    def get_transcript(video_id):
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([t['text'] for t in transcript])

    def get_summary(transcript):
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        chunk_size = 1000
        chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]
        summaries = []
        for chunk in chunks:
            summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
            summaries.append(summary[0]['summary_text'])
        final_summary = ' '.join(summaries)
        return final_summary
    ```

- **Run the Application:**

    ```python
    if __name__ == '__main__':
        app.run(debug=True)
    ```