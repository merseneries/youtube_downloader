import logging
from pathlib import Path
from pytube import YouTube, Stream
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """
    Class that download a video from YouTube with a given URL. It downloads the video and audio separately and then
    combines them using the ffmpeg tool.
    """

    def __init__(
        self,
        url: str,
        resolution: str = "1080",
        video_type: str = "mp4",
        audio_type: str = "webm",
        fps: int = 30,
        output_dir: str = Path(__name__).parent / "data",
    ):
        self.url = url
        self._youtube = YouTube(url)
        self._all_streams = self._get_all_streams()
        self._video_stream = None
        self._audio_stream = None
        # if dry_run don't check these params:
        self.resolution = resolution
        self.video_type = video_type
        self.audio_type = audio_type
        self.fps = fps
        self.output_dir = output_dir

    @property
    def resolution(self):
        return self._resolution

    @property
    def video_type(self):
        return self._video_type

    @property
    def audio_type(self):
        return self._audio_type

    @property
    def fps(self):
        return self._fps

    @resolution.setter
    def resolution(self, resolution: str):
        """Set the resolution attribute if it is available"""
        resolution = resolution.lower()
        resolution = resolution + "p" if "p" not in resolution else resolution
        # Check for attribute?
        available_video_resolutions = set(
            [stream.resolution for stream in self.get_video_streams()]
        )

        if resolution not in available_video_resolutions:
            raise ValueError(
                f"Resolution '{resolution}' is not available for this video.\nAvailable resolutions: {available_video_resolutions}"
            )
        self._resolution = resolution

    @video_type.setter
    def video_type(self, video_type: str):
        """Set the video type attribute if it is available"""
        video_type = (
            video_type.replace("video/", "") if "video/" in video_type else video_type
        )
        # Check for attribute?
        available_video_types = set(
            [
                stream.mime_type.replace("video/", "")
                for stream in self.get_video_streams()
            ]
        )

        if video_type not in available_video_types:
            raise ValueError(
                f"Video type '{video_type}' is not available for this video.\nAvailable video types: {available_video_types}"
            )
        self._video_type = "video/" + video_type

    @audio_type.setter
    def audio_type(self, audio_type: str):
        """Set the audio type attribute if it is available"""
        audio_type = (
            audio_type.replace("audio/", "") if "audio/" in audio_type else audio_type
        )
        # Check for attribute?
        available_audio_types = set(
            [
                stream.mime_type.replace("audio/", "")
                for stream in self.get_audio_streams()
            ]
        )

        if audio_type not in available_audio_types:
            raise ValueError(
                f"Audio type '{audio_type}' is not available for this video.\nAvailable audio types: {available_audio_types}"
            )
        self._audio_type = "audio/" + audio_type

    @fps.setter
    def fps(self, fps: int):
        """Set the fps attribute if it available"""
        try:
            fps = fps if isinstance(fps, int) else int(fps)
        except ValueError as error:
            logger.info("FPS value should be a digit.")
            logger.error(error)

        # Check for attribute?
        available_fps = set([stream.fps for stream in self.get_video_streams()])

        if fps not in available_fps:
            raise ValueError(
                f"FPS '{fps}' is not available for this video.\nAvailable FPS: {fps}"
            )
        self._fps = fps

    def _get_all_streams(self) -> List[Stream]:
        return self._youtube.streams

    def get_filtered_streams(self, params: Dict[str, Union[str, int, bool]]):
        return self._all_streams.filter(**params)

    def get_audio_streams(self) -> List[Stream]:
        return self._all_streams.filter(only_audio=True)

    def get_video_streams(self) -> List[Stream]:
        return self._all_streams.filter(only_video=True)

    def get_adaptive_video_streams(self) -> List[Stream]:
        return self._all_streams.filter(only_video=True, adaptive=True)

    def _set_streams(self):
        """Set stream for video and audio that will be dowloaded"""
        audio_params = {"mime_type": self.audio_type}
        video_params = {
            "resolution": self.resolution,
            "mime_type": self.video_type,
            "fps": self.fps,
        }

        video_streams = self.get_filtered_streams(video_params)
        if not video_streams:
            raise ValueError(f"Video stream with these parameters {video_params} not found.")

        audio_streams = self.get_filtered_streams(audio_params)
        audio_streams = sorted(
            audio_streams, key=lambda stream: int(stream.abr.replace("kbps", ""))
        )
        if not audio_params:
            raise ValueError(f"Audio stream with these parameters {audio_params} not found.")

        self._video_stream = video_streams[0]
        self._audio_stream = audio_streams[-1]

    def download_streams(self):
        """Download streams data"""
        self._set_streams()
        self._video_stream.download(output_path=self.output_dir, filename_prefix="video_")
        self._audio_stream.download(output_path=self.output_dir, filename_prefix="audio_")
