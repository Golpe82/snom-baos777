import asyncio
import logging

import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor

VALUES = ["on", "off"]


class HTTPKNXDispatcher:
    def __init__(self, subscripted_leds, status, groupaddress):
        self.subscriptions = subscripted_leds
        self.status = status
        self.groupaddress = groupaddress
        _new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_new_loop)
        self._loop = asyncio.get_event_loop()
        self._future = asyncio.ensure_future(self._get_data_asynchronous())

    async def _get_data_asynchronous(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            with requests.Session() as session:
                loop = asyncio.get_event_loop()

                if self.status in VALUES:
                    tasks = [
                        loop.run_in_executor(
                            executor,
                            self._fetch,
                            *(
                                session,
                                led.__getattribute__(
                                    f"on_change_xml_for_{self.status}_url"
                                ),
                            ),  # Allows us to pass in multiple arguments to `fetch`
                        )
                        for led in self.subscriptions
                    ]
                    for response in await asyncio.gather(*tasks):
                        logging.info(response.status_code)
                else:
                    logging.error(
                        f"wrong value {self.status} for groupaddress {self.groupaddress}"
                    )

    def _fetch(self, session, xml_url):
        with session.get(xml_url, timeout=5) as response:
            if response.status_code == 401:
                response = self._http_get_with_auth(xml_url)
            if response.status_code == 401:
                response = self._http_get_with_auth(xml_url, auth="basic")

            return response

    def _http_get_with_auth(self, url, auth="digest"):
        phone_wui_user = "admin"
        phone_wui_passwd = "7666"

        if auth == "digest":
            return requests.get(
                url,
                auth=HTTPDigestAuth(phone_wui_user, phone_wui_passwd),
            )
        elif auth == "basic":
            return requests.get(
                url,
                auth=HTTPBasicAuth(phone_wui_user, phone_wui_passwd),
            )

        response = requests.Response()
        response.status_code = 400
        content = f"Invalid authentication method {auth}"
        response._content = content.encode()

        return response

    def dispatch(self):
        self._loop.run_until_complete(self._future)
