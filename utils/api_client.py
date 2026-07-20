# -*- coding: utf-8 -*-
"""ApiClient：基于 requests.Session 的轻量 API 封装，统一 base_url、鉴权、超时。"""
import requests


class ApiClient:
    def __init__(self, base_url: str, api_key: str = "", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key
        self.session.headers.update(headers)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: dict = None) -> requests.Response:
        return self.session.get(self._url(path), params=params, timeout=self.timeout)

    def post(self, path: str, json: dict = None) -> requests.Response:
        return self.session.post(self._url(path), json=json, timeout=self.timeout)

    def put(self, path: str, json: dict = None) -> requests.Response:
        return self.session.put(self._url(path), json=json, timeout=self.timeout)

    def patch(self, path: str, json: dict = None) -> requests.Response:
        return self.session.patch(self._url(path), json=json, timeout=self.timeout)

    def delete(self, path: str) -> requests.Response:
        return self.session.delete(self._url(path), timeout=self.timeout)

    def close(self):
        self.session.close()
