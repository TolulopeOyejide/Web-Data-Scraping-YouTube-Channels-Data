import pandas as pd
from googleapiclient.discovery import build

def fetch_and_save_videos(api_key, search_term, max_results=3000):
    """
    Fetches YouTube videos and their channel details, then saves them to an Excel file.
    """
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)

    print(f"Searching for videos with the keyword: '{search_term}'...")

    # This list will store the dictionaries for our final Excel file
    all_video_data = []
    # This dictionary will act as our cache to store channel data
    channel_data_cache = {}
    next_page_token = None

    while len(all_video_data) < max_results:
        try:
            search_response = youtube.search().list(
                q=search_term,
                part="snippet",
                type="video",
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            channel_ids_to_fetch = set()
            video_items = search_response.get("items", [])
            
            # First, gather all the unique channel IDs from the search results
            for item in video_items:
                channel_id = item["snippet"]["channelId"]
                if channel_id not in channel_data_cache:
                    channel_ids_to_fetch.add(channel_id)

            # Now, fetch details for all the new, unique channels at once
            if channel_ids_to_fetch:
                # We can request up to 50 channel details in a single API call
                channel_response = youtube.channels().list(
                    part="snippet,statistics,brandingSettings",
                    id=",".join(channel_ids_to_fetch)
                ).execute()

                # Store the fetched channel details in our cache
                for item in channel_response.get("items", []):
                    channel_id = item["id"]
                    stats = item.get("statistics", {})
                    # Some channels hide their subscriber count
                    subscriber_count = stats.get("subscriberCount") if not stats.get("hiddenSubscriberCount", False) else "Hidden"
                    
                    # Extracting the channel handle (customUrl)
                    channel_handle = item.get("snippet", {}).get("customUrl", "N/A")

                    channel_data_cache[channel_id] = {
                        "subscribers": subscriber_count,
                        "description": item.get("snippet", {}).get("description", "N/A"),
                        "country": item.get("brandingSettings", {}).get("channel", {}).get("country", "N/A"),
                        "handle": channel_handle  # Store the handle here
                    }

            # Finally, combine video and channel data
            for item in video_items:
                video_title = item["snippet"]["title"]
                video_id = item["id"]["videoId"]
                channel_id = item["snippet"]["channelId"]
                channel_title = item["snippet"]["channelTitle"] # This is the channel's display name
                
                # Get the channel details from our cache
                channel_details = channel_data_cache.get(channel_id, {})

                # Prepare the data row, now including Channel Handle and excluding Channel ID
                data_row = {
                    "Video Title": video_title,
                    "Channel Name": channel_title,
                    "Channel Handle": channel_details.get("handle", "N/A"), # <-- ADDED THIS LINE
                    "Subscribers": channel_details.get("subscribers", "N/A"),
                    "Channel Description": channel_details.get("description", "N/A"),
                    "Channel Country": channel_details.get("country", "N/A"),
                    "Video Link": f"https://www.youtube.com/watch?v={video_id}",
                    # "Channel ID": channel_id # <-- REMOVED/COMMENTED OUT THIS LINE
                }
                all_video_data.append(data_row)

            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                print("No more results found.")
                break
            
            print(f"Collected data for {len(all_video_data)} videos so far...")

        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print("\n--- Search Complete ---")

    if not all_video_data:
        print("No data was collected. Exiting.")
        return

    print(f"Successfully fetched data for {len(all_video_data)} videos.")
    
    # Use pandas to create a DataFrame and save it to Excel
    print("Saving data to Excel file...")
    df = pd.DataFrame(all_video_data)
    # The 'index=False' prevents pandas from writing row numbers into the file
    df.to_excel("youtube_results.xlsx", index=False, engine="openpyxl")
    print("Successfully saved results to youtube_results.xlsx")


if __name__ == "__main__":
    API_KEY = "AIzaSyAALjZ7qOE_pUMIKLMTIG59T2kHqUYhsIk" 
    #API_KEY = "AIzaSyAllTySgSi2x-Etu6TzyPZNtpiEUS1Uj1w"
    #API_KEY =  "AIzaSyCJatRJ7-hyeZP27vYo94_K_HTj-9dkuY4" 

    SEARCH_KEYWORD = "How to add professional lower thirds and titles on mobile for free"
    VIDEOS_TO_FETCH = 1500

    fetch_and_save_videos(API_KEY, SEARCH_KEYWORD, VIDEOS_TO_FETCH)