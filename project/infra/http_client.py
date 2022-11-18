import aiohttp
from config import settings
from logger import log
from pydantic import AnyHttpUrl, BaseModel


class ResponseAPI(BaseModel):
    element: dict | list[dict]
    status: int


# log = get_logger(__name__)


class HTTPClient:
    __instance = None
    client_session = None
    __base_url: AnyHttpUrl = settings.url_api

    def __new__(cls, url=None):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        if cls.client_session is None:
            try:
                if url is not None:
                    cls.base_url = url
                cls.client_session = aiohttp.ClientSession(base_url=cls.__base_url)
            except:
                raise Exception("Aiohttp session failed to open")
        log.debug("HTTP Client is opening")
        return cls.__instance

    @classmethod
    def set_url(cls, url: AnyHttpUrl):
        cls.__base_url: AnyHttpUrl = url

    @classmethod
    def is_session_open(cls):
        if cls.client_session is None:
            raise Exception("Aiohttp session is not open")

    async def __aenter__(self):
        HTTPClient.is_session_open()
        return HTTPClient.__instance

    async def __aexit__(self, *args):
        pass
        # await HTTPClient.close()

    @classmethod
    async def close(cls):
        try:
            cls.is_session_open()
        except:
            raise Exception("Aiohttp session is already closed")
        await cls.client_session.close()
        log.debug("HTTP Client is closing")
        cls.client_session = None

    @classmethod
    async def post(cls, url, data: dict):
        cls.is_session_open()
        async with cls.client_session.post(url, json=data) as response:
            log.info(f"POST: url accessed {response.url}, status: {response.status}")
            return ResponseAPI(element=await response.json(), status=response.status)

    @classmethod
    async def get(cls, url, params: dict = None, id_element: int | str = None):
        cls.is_session_open()
        if id_element is not None:
            url += f"/{id_element}"
        if params is None:
            params = {}
        async with cls.client_session.get(url=url, params=params) as response:
            log.info(f"GET: url accessed {response.url}, status: {response.status}")
            return ResponseAPI(element=await response.json(), status=response.status)

    @classmethod
    async def patch(cls, url, data: dict, id_element: int = None):
        cls.is_session_open()
        if id_element is not None:
            url += f"/{id_element}"
        async with cls.client_session.patch(url=url, json=data) as response:
            log.info(f"PATCH: url accessed {response.url}, status: {response.status}")
            return ResponseAPI(element=await response.json(), status=response.status)

    @classmethod
    async def delete(cls, url, id_element: int = None):
        cls.is_session_open()
        if id_element is not None:
            url += f"/{id_element}"
        async with cls.client_session.delete(url=url) as response:
            log.info(f"DELETE: url accessed {response.url}, status: {response.status}")
            return ResponseAPI(element=await response.json(), status=response.status)
