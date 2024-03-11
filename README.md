# YouTube Comments Analyzer

This script allows you to fetch comments from YouTube videos using the YouTube Data API and generate insights based on the comments using the Google GenAI API.

## Setup

1. **Create Virtual Environment:**
    - It's recommended to create a virtual environment to manage dependencies.
        ```bash
        python -m venv env
        source env/bin/activate  # On Linux/Mac
        .\env\Scripts\activate   # On Windows
        ```

2. **Install Dependencies:**
    - Install the required Python packages specified in `requirements.txt`.
        ```bash
        pip install -r requirements.txt
        ```

3. **Obtain API Keys:**
    - You need two API keys: one for the YouTube Data API and another for the Google GenAI API.
    - Obtain a YouTube Data API key from the [Google Cloud Console](https://console.cloud.google.com/).
    - Obtain a Google GenAI API key from the [Google GenAI website](https://cloud.google.com/generative-ai).
   
4. **Set Environment Variables:**
    - Export the API keys as environment variables:
        ```bash
        export YOUTUBE_API_KEY="your_youtube_api_key"
        export GEMINI_API_KEY="your_geminai_api_key"
        ```

## Usage

1. **Get Video IDs:**
    - Replace the `youtube_video_ids` list in the script with the YouTube video IDs you want to analyze.
    - You can obtain video IDs from the YouTube video URL. It is the string after `v=` in the URL.
  
2. **Running the Script:**
    - Run the script `youtube_comments_analyzer.py`.
    - It will fetch comments from the specified YouTube videos and store them in CSV files in the `youtube` directory.
    - Then, it generates insights based on the comments using the Google GenAI API and saves them in the `youtube/insights.md` file.

3. **Interpreting Insights:**
    - The generated insights will provide you with an analysis of the comments for each video.
    - You can use these insights to identify major issues or improvement points regarding the topic of the videos.

4. **Customizing Insights Prompt:**
    - You can customize the prompt used for generating insights by modifying the `user_prompt` parameter in the script.
    - Change the prompt to fit your specific needs for analyzing comments.
    - Example prompt:
        ```python
        user_prompt="""THE PREVIOUS DATA CONSISTS OF COMMENTS FROM A YOUTUBE OPINION VIDEO. FIND MAJOR ISSUES OR IMPROVEMENT POINTS AMONG THOSE COMMENTS AND LIST THEM. BE AS SPECIFIC AS POSSIBLE."""
        ```

## Example

```bash
python youtube_comments_analyzer.py
