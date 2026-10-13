import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


class FetchError(Exception):
    """Safe, user-facing error without response bodies or request headers."""


class AppStoreClient:
    def __init__(self, network: dict, country: str = "cn"):
        self.network = network
        self.country = country
        self.last_request = None

    def _get(self, endpoint: str, params: dict) -> dict:
        url = f"https://itunes.apple.com/{endpoint}?{urlencode(params)}"
        reason = "网络错误"
        for _ in range(self.network["retries"] + 1):
            if self.last_request is not None:
                delay = self.network["request_interval_seconds"] - (time.monotonic() - self.last_request)
                if delay > 0:
                    time.sleep(delay)
            self.last_request = time.monotonic()
            try:
                request = Request(url, headers={"User-Agent": "pm-goldfinger/0.1", "Accept": "application/json"})
                with urlopen(request, timeout=self.network["timeout_seconds"]) as response:
                    payload = json.load(response)
                if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
                    raise ValueError("Invalid results")
                return payload
            except HTTPError as error:
                reason = f"HTTP {error.code}"
            except (URLError, TimeoutError, OSError):
                reason = "网络错误或超时"
            except (ValueError, UnicodeError):
                reason = "响应格式错误"
        raise FetchError(f"App Store 请求失败，已重试 2 次（{reason}）。")

    def search(self, term: str) -> list[dict]:
        data = self._get("search", {"term": term, "country": self.country, "entity": "software", "limit": 5})
        return [{key: row.get(key) for key in ("trackId", "trackName", "sellerName", "bundleId", "trackViewUrl")}
                for row in data["results"] if isinstance(row, dict) and row.get("trackId")]

    def lookup(self, app: dict) -> dict:
        data = self._get("lookup", {"id": app["app_id"], "country": self.country})
        matches = [row for row in data["results"] if isinstance(row, dict)
                   and row.get("trackId") == app["app_id"] and row.get("wrapperType") == "software"]
        if len(matches) != 1:
            raise FetchError(f"{app['name']}：中国区未返回唯一的已确认 App，保留原有快照与报告。")
        row = matches[0]
        url = row.get("trackViewUrl", "")
        if not isinstance(url, str) or urlsplit(url).scheme != "https" or urlsplit(url).hostname != "apps.apple.com":
            raise FetchError(f"{app['name']}：App Store 链接无效。")
        version = row.get("version")
        if not isinstance(version, str) or not version.strip():
            raise FetchError(f"{app['name']}：版本号缺失。")
        rating, count = row.get("averageUserRating"), row.get("userRatingCount")
        if rating is not None and (type(rating) not in (int, float) or not math.isfinite(rating) or not 0 <= rating <= 5):
            raise FetchError(f"{app['name']}：评分格式错误。")
        if count is not None and (type(count) is not int or count < 0):
            raise FetchError(f"{app['name']}：评分人数格式错误。")
        notes, release_date = row.get("releaseNotes") or "", row.get("currentVersionReleaseDate") or ""
        if not isinstance(notes, str) or not isinstance(release_date, str):
            raise FetchError(f"{app['name']}：更新说明或日期格式错误。")
        return {
            "name": app["name"], "app_id": app["app_id"], "version": version,
            "release_notes": notes, "release_date": release_date,
            "rating": rating, "rating_count": count, "url": url,
        }
