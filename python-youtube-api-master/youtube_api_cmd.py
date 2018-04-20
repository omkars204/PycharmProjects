import json
import sys
import pandas as pd
from urllib import *
import argparse
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen

YOUTUBE_COMMENT_URL = 'https://www.googleapis.com/youtube/v3/commentThreads'
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'


class YouTubeApi():

    def load_comments(self, mat, comments, vid):
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            author = comment["snippet"]["authorDisplayName"]
            text = comment["snippet"]["textDisplay"]
            # print("Comment by {}: {}".format(author, text))
            comments.append({'vid': vid, 'author': author, 'comment': text})

    def get_video_comment(self, vid):
        mxRes = 20
        parms = {
            'part': 'snippet,replies',
            'maxResults': mxRes,
            'videoId': vid,
            'textFormat': 'plainText',
            'key': 'AIzaSyCoPmkDC_7P87VpdyfqDLxoopgKm8tbKC4'
        }

        try:
            comments = []
            matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
            i = 2
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")
            print("\nPage : 1")
            print("------------------------------------------------------------------")
            self.load_comments(mat, comments, vid)
            while nextPageToken and i <= 10:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_COMMENT_URL, parms)
                mat = json.loads(matches)
                nextPageToken = mat.get("nextPageToken")
                print("\nPage : ", i)
                print("------------------------------------------------------------------")
                self.load_comments(mat, comments, vid)
                i += 1
            return comments
        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot Open URL or Fetch comments at a moment")

    def load_search_res(self, search_response, videos):
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                title = search_result["snippet"]["title"]
                vid = search_result["id"]["videoId"]
                videos.append({'title': title, 'id': vid})

    def search_keyword(self, search):

        parser = argparse.ArgumentParser()
        mxRes = 10
        region = "IN"
        parms = {
            'q': search,
            'part': 'id,snippet',
            'maxResults': mxRes,
            'regionCode': region,
            'key': 'AIzaSyCoPmkDC_7P87VpdyfqDLxoopgKm8tbKC4'

        }

        try:
            matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

            search_response = json.loads(matches)
            i = 2

            nextPageToken = search_response.get("nextPageToken")

            videos = []
            print("\nPage : 1 --- Region : {}".format(region))
            print("------------------------------------------------------------------")
            self.load_search_res(search_response, videos)
            while nextPageToken and i <= 10:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

                search_response = json.loads(matches)
                nextPageToken = search_response.get("nextPageToken")
                print("Page : {} --- Region : {}".format(i, region))
                print("------------------------------------------------------------------")

                self.load_search_res(search_response, videos)
                i += 1

            return videos

        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot Open URL or Fetch comments at a moment")

    def channel_videos(self):

        def load_channel_vid(self):

            for search_result in search_response.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                    videos.append("{} ({})".format(search_result["snippet"]["title"],
                                                   search_result["id"]["videoId"]))

            print("###Videos:###\n", "\n".join(videos), "\n")

        parser = argparse.ArgumentParser()
        mxRes = 20
        parser.add_argument("--sc", help="calls the search by channel by keyword function", action='store_true')
        parser.add_argument("--channelid", help="Search Term", default="Srce Cde")
        parser.add_argument("--max", help="number of results to return")
        parser.add_argument("--key", help="Required API key")

        args = parser.parse_args()

        if not args.max:
            args.max = mxRes

        if not args.channelid:
            exit("Please specify channelid using the --channelid= parameter.")

        if not args.key:
            exit("Please specify API key using the --key= parameter.")

        parms = {
            'part': 'id,snippet',
            'channelId': args.channelid,
            'maxResults': args.max,
            'key': args.key
        }

        try:
            matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

            search_response = json.loads(matches)

            videos = []
            i = 2

            nextPageToken = search_response.get("nextPageToken")
            print("\nPage : 1")
            print("------------------------------------------------------------------")

            load_channel_vid(self)

            while nextPageToken:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(YOUTUBE_SEARCH_URL, parms)

                search_response = json.loads(matches)
                nextPageToken = search_response.get("nextPageToken")
                print("Page : ", i)
                print("------------------------------------------------------------------")

                load_channel_vid(self)

                i += 1

        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot Open URL or Fetch comments at a moment")

    def openURL(self, url, parms):
        f = urlopen(url + '?' + urlencode(parms))
        data = f.read()
        f.close()
        matches = data.decode("utf-8")
        return matches


def main():
    y = YouTubeApi()

    if len(sys.argv) > 1:
        if str(sys.argv[1]) == "--s":
            query = input('search term')
            results = y.search_keyword(query)
            print(results)
        elif str(sys.argv[1]) == "--c":
            vid = input('pass video id')
            y.get_video_comment(vid)
        elif str(sys.argv[1]) == "--sc":
            y.channel_videos()
        else:
            print(
                "Invalid Arguments\nAdd --s for searching video by keyword after the filename\nAdd --c to list comments after the filename\nAdd --sc to list vidoes based on channel id")
    else:
        # main code
        query = input('search term')
        results = y.search_keyword(query)
        videosDf = pd.DataFrame(results)
        print(videosDf)
        videosDf.to_csv(query + '_videos.csv')
        dfs = []
        for item in results[:3]:
            video_id = item['id']
            comments = y.get_video_comment(video_id)
            comments_df = pd.DataFrame(comments)
            dfs.append(comments_df)
            print(comments_df)
        all_comments = pd.concat(dfs)
        all_comments.to_csv(query + '_comments.csv')


if __name__ == '__main__':
    main()
