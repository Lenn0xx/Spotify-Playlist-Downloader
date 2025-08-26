from requests import get, post
from googleapiclient.discovery import build
from dotenv import load_dotenv
import json
import os
import base64
import yt_dlp

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

service = build("youtube", "v3", developerKey="AIzaSyDC_DtMC7E_NZmhTZOhV0qa8WN1VmkSkwM")

def get_token():
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_headers(token):
    return {"Authorization": "Bearer " + token}

def get_playlist_items(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_headers(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    print(json_result)

def main():
    playlist_url = input("Playlist URL (MUST BE PUBLIC): ")
    html = get(playlist_url)
    soup = BeautifulSoup(html.text, 'lxml')
    songs = soup.find_all("span", class_='ListRowTitle__LineClamp-sc-1xe2if1-0 jjpOuK')
    title = soup.find("h1", class_="e-91000-text encore-text-title-medium gj6rSoF7K4FohS2DJDEm")

    with open("playlist.txt", "r+") as f:
        f.truncate(0)
        f.write(f"{title.text}\n")
        for i in range(len(songs)):
            f.write(f"{songs[i].text}\n")

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/135.0.0.0 Safari/537.36',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def search(q):
    request = service.search().list(
        part="snippet",      # Required field: tells API what data you want
        q=q,     # Your search query
        type="video",        # Only return videos (not channels/playlists)
        maxResults=5         # Number of results to return
    )
    response = request.execute()

    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"{title}: {url}")

token = get_token()
get_playlist_items(token, "37i9dQZF1DXcBWIGoYBM5M")
