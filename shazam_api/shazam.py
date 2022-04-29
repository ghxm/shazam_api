"""Main module."""
import requests
from io import BytesIO
import base64
import time
from pydub import AudioSegment



# shazam api object
class ShazamApi:

    def __init__(self, api_key, api_url = "https://rapidapi.p.rapidapi.com/", api_host = "shazam.p.rapidapi.com"):

        self.api_url = api_url
        self.api_key = api_key
        self.api_host = api_host

        self.headers = {
	        "x-rapidapi-host": self.api_host,
	        "x-rapidapi-key": self.api_key
        }



    def _get(self, url, querystring):
        """
        Get from the api
        :param url:
        :param querystring:
        :return: API response
        """

        # append api url if not already there
        if not url.startswith(self.api_url):
            url = self.api_url + url

        headers = self.headers

        requests.request("GET", url, headers=headers, params=querystring)

    def _post(self, url, data, headers=None):
        """
        Post to the api
        """

        if headers is None:
            headers = self.headers

        # append api url if not already there
        if not url.startswith(self.api_url):
            url = self.api_url + url

        response = requests.request("POST", url, data=data, headers=headers)

        return response

    def _record(self, file_path, rec_seconds=10):
        """
        Record the song from the file path
        """

        # record stream from url for 10 seconds

        print("Recording from stream {}".format(file_path))

        r = requests.get(file_path, stream=True)

        recording = BytesIO()

        start_time = time.time()

        for block in r.iter_content(1024):
            recording.write(block)
            if time.time() - start_time > rec_seconds:
                recording.seek(0)
                break

        sound = AudioSegment.from_mp3(recording)
        sound = sound.set_channels(1)

        return base64.b64encode(sound.raw_data)


    # api channels

    def detect(self, file_path, v2 = True, rec_seconds=10):
        """
        Detect the song from the file path
        """

        headers = self.headers
        headers['content-type'] = "text/plain"

        if file_path.startswith("http"):

            recording = self._record(file_path=file_path, rec_seconds=rec_seconds)

            response = self._post(url = "songs/detect", data = recording, headers = headers)
        else:
            recording = base64.b64encode(open(file_path, "rb").read())

            if v2:
                response = self._post(url = "songs/v2/detect", data = recording, headers = headers)
            else:
                response=self._post(url = "songs/detect", data = recording, headers = headers)

        return response


