import json
import os
import traceback
from typing import Dict, List, Optional
from time import sleep

import pandas as pd
from googleapiclient.discovery import build
import google.generativeai as genai

# Replace with your API key (or keys) obtained from Google Cloud Platform
YOUTUBE_API_KEY: str = os.environ.get("YOUTUBE_API_KEY")
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY")
# The local directory in which comments will be downloaded as CSV files. The route of the folder will be relative to this file.
OUTPUT_DIRECTORY: str = "youtube"


def get_comments(video_id: str) -> List[dict]:
    """
    Fetches comments of a YouTube video using its video ID.

    Args:
        video_id (str): The YouTube video ID.

    Returns:
        List[dict]: List of comments extracted from the video.
    """
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    if not os.path.exists(OUTPUT_DIRECTORY):
        # If not, create it
        os.makedirs(OUTPUT_DIRECTORY)

    request = youtube.commentThreads().list(
        part="snippet,replies", videoId=video_id, textFormat="plainText"
    )

    df = pd.DataFrame(columns=["comment", "replies", "date", "user_name"])

    while request:
        replies = []
        comments = []
        dates = []
        user_names = []

        try:
            response = request.execute()

            for item in response["items"]:
                # Extracting comments
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)

                user_name = item["snippet"]["topLevelComment"]["snippet"][
                    "authorDisplayName"
                ]
                user_names.append(user_name)

                date = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                dates.append(date)

                # counting number of reply of comment
                replycount = item["snippet"]["totalReplyCount"]

                # if reply is there
                if replycount > 0:
                    # append empty list to replies
                    replies.append([])
                    # iterate through all reply
                    for reply in item["replies"]["comments"]:
                        # Extract reply
                        reply = reply["snippet"]["textDisplay"]
                        # append reply to last element of replies
                        replies[-1].append(reply)
                else:
                    replies.append([])

            # create new dataframe
            df2 = pd.DataFrame(
                {
                    "comment": comments,
                    "replies": replies,
                    "user_name": user_names,
                    "date": dates,
                }
            )
            df = pd.concat([df, df2], ignore_index=True)
            df.to_csv(
                f"./youtube/{video_id}_user_comments.csv", index=False, encoding="utf-8"
            )
            sleep(2)
            request = youtube.commentThreads().list_next(request, response)
            print("Iterating through next page")
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            print("Sleeping for 10 seconds")
            sleep(10)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding="utf-8")
            break
    return comments


def fetch_videos(video_ids: List[str]) -> None:
    """
    Fetches comments for a list of YouTube videos.

    Args:
        video_ids (List[str]): List of YouTube video IDs.
    """
    for video_id in video_ids:
        print(f"================== {video_id} =============================")
        comments = get_comments(video_id)
        for comment in comments:
            # Process comments for further analysis or storage
            # ...
            # You can modify this section to perform specific actions on the comments
            # For example, store them in a database, etc.
            print(comment)


def read_comments_from_csv(filename: str) -> Optional[Dict[str, List[str]]]:
    """
    Reads comments, replies, usernames, and dates from a YouTube comments CSV file.

    Args:
        filename (str): Path to the CSV file containing YouTube comments data.

    Returns:
        Optional[Dict[str, List[str]]]: A dictionary containing lists of comments, replies, usernames, and dates.
    """
    try:
        df = pd.read_csv(filename)
        comments = df["comment"].tolist()
        replies = df["replies"].tolist()
        usernames = df["user_name"].tolist()
        dates = df["date"].tolist()
        return {
            "comments": comments,
            "replies": replies,
            "usernames": usernames,
            "dates": dates,
        }
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None


def get_insights(user_promt: str, video_ids: List[str]) -> None:
    """
    Generates insights using comments data of YouTube videos and Gemini Pro model.

    Args:
        user_promt (str): The prompt to be used for generating insights.
        video_ids (List[str]): List of YouTube video IDs.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")

    for video_id in video_ids:
        print(f"================== {video_id} =============================")

        # Example usage (replace with your actual filename)
        filename = f"./youtube/{video_id}_user_comments.csv"
        comments_data = read_comments_from_csv(filename)

        comments_promt = []
        if comments_data:
            for i in range(len(comments_data["comments"])):
                print(f"Comment: {comments_data['comments'][i]}")
                print(f"Comment replies: {comments_data['replies'][i]}")
                print(f"Username: {comments_data['usernames'][i]}")
                print(f"Date: {comments_data['dates'][i]}\n")
                comments_promt.append(
                    {
                        "comment": comments_data["comments"][i],
                        "comment_replies": comments_data["replies"][i],
                    }
                )
            else:
                print("No comments data found.")
        prompt = json.dumps(comments_promt) + "\n" + user_promt
        response = model.generate_content(prompt)
        print(response.text)
        # The file is in "append" mode so all insights will be appended at the end
        with open(f"{OUTPUT_DIRECTORY}/insights.md", "a") as output_file:
            output_file.write(f"Video: {video_id}\n")
            output_file.write(response.text + "\n")
            output_file.write("------------------------------------------------")
            output_file.write("\n")


if __name__ == "__main__":
    # Replace with your list of video IDs
    youtube_video_ids = [
        "bx3hfXczva8",
        "cZYo4RgRd0Q",
        "7BBrt0kmDnk",
    ]
    if YOUTUBE_API_KEY is None or GEMINI_API_KEY is None:
        print(
            "Error: Please set YOUTUBE_API_KEY and GEMINI_API_KEY environment variables."
        )
    else:
        fetch_videos(video_ids=youtube_video_ids)
        # change the promt to feat your needs
        get_insights(
            user_promt="""THE PREVIOUS DATA CONSISTS OF COMMENTS FROM A YOUTUBE 
            OPINION VIDEO. FIND MAJOR ISSUES OR IMPROVEMENT POINTS AMONG THOSE 
            COMMENTS AND LIST THEM. BE AS SPECIFIC AS POSSIBLE.""",
            video_ids=youtube_video_ids,
        )
