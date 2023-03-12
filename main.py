from src.downloader import YouTubeDownloader


URL = "https://www.youtube.com/watch?v=qCTHEFMrbWI&ab_channel=Merseneries"
youtube_downloader = YouTubeDownloader(URL)
youtube_downloader.download_streams()
