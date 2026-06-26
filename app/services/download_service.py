import re
import aiohttp
from typing import Optional, Dict, Any

class DownloadScraperEngine:
    @staticmethod
    def identify_platform(url: str) -> Optional[str]:
        patterns = {
            "tiktok": r"(v[mt]\.tiktok\.com|www\.tiktok\.com)",
            "instagram": r"(www\.)?instagram\.com",
            "facebook": r"(www\.|fb\.)?facebook\.com",
            "pinterest": r"(pin\.it|www\.pinterest\.com)",
            "spotify": r"open\.spotify\.com",
            "terabox": r"(terabox\.com|neofiles\.com|4shared\.com|mirrobox\.com)"
        }
        for engine_name, regex in patterns.items():
            if re.search(regex, url):
                return engine_name
        return None

    @classmethod
    async def process_download(cls, platform: str, url: str) -> Optional[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            try:
                if platform == "tiktok":
                    async with session.get(f"https://www.tikwm.com/api/?url={url}") as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            d = res.get("data", {})
                            return {"direct_url": d.get("play"), "title": d.get("title", "TikTok Video"), "thumb": d.get("cover")}
                            
                elif platform == "instagram":
                    async with session.get(f"https://igram.site/api/instagram?url={url}") as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            if isinstance(res, list) and len(res) > 0:
                                return {"direct_url": res[0].get("url"), "title": "Instagram Media", "thumb": res[0].get("thumbnail")}
                                
                elif platform == "facebook":
                    api_url = f"https://serverless-tooly-gateway-6n4h522y.ue.gateway.dev/facebook/video?url={url}"
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            videos = res.get("videos", {})
                            direct = videos.get("hd", {}).get("url") or videos.get("sd", {}).get("url")
                            return {"direct_url": direct, "title": "Facebook Video", "thumb": None}
                            
                elif platform == "pinterest":
                    async with session.get(f"https://api.pinssaver.com/pin?url={url}") as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            return {"direct_url": res.get("data", {}).get("src", {}).get("orig"), "title": "Pinterest Media", "thumb": None}
                            
                elif platform == "spotify":
                    async with session.get(f"https://spotyloader.com/api/spotify/info?url={url}") as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            post = res.get("post", {})
                            return {"direct_url": post.get("preview_url"), "title": f"{post.get('name')} - {post.get('artist')}", "thumb": post.get("image")}
                            
                elif platform == "terabox":
                    # Correctly structured to append your explicit token parameter natively
                    api_url = f"https://teradown-dzv3.onrender.com/api?url={url}&ndus=Y2t6_i7teHuiX-uHDssg3XhTPleotTOyL1Jf5tPV"
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            res = await resp.json()
                            return {"direct_url": res.get("download"), "title": res.get("name", "Terabox File"), "thumb": res.get("thumbnail")}
            except Exception:
                return None
        return None
