import json
import logging
import urllib.parse

import requests

logger = logging.getLogger("qualifire")


class QualifireLogger:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        version: str,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._version = version
        self._headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "X-qualifire-key": self._api_key,
            "X-qualifire-sdk-version": self._version,
        }

    def log_request(self, body: dict) -> None:
        q_response = requests.post(
            urllib.parse.urljoin(self._base_url, "/api/intake"),
            data=json.dumps(
                {
                    "body": body,
                }
            ),
            headers=self._headers,
            timeout=300,
        )

        return q_response.json()

    def log_response(self, id: str, model: str, body: dict) -> None:

        requests.patch(
            urllib.parse.urljoin(self._base_url, "/api/intake"),
            data=json.dumps(
                {
                    "createdCallId": id,
                    "model": model,
                    "body": body,
                },
            ),
            headers=self._headers,
            timeout=300,
        )
