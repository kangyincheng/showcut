import json
import urllib.request
import urllib.parse
import hashlib
import random
import time


class Translator:
    def __init__(self):
        pass

    def translate_baidu(self, text, from_lang="auto", to_lang="zh"):
        try:
            import urllib.request
            import urllib.parse
            import json
            import hashlib
            import random

            appid = ""
            secret_key = ""

            if not appid or not secret_key:
                return self._translate_free(text, from_lang, to_lang)

            salt = str(random.randint(32768, 65536))
            sign = appid + text + salt + secret_key
            sign = hashlib.md5(sign.encode()).hexdigest()

            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            params = {
                "q": text,
                "from": from_lang,
                "to": to_lang,
                "appid": appid,
                "salt": salt,
                "sign": sign,
            }

            data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read().decode("utf-8"))

            if "trans_result" in result:
                translations = [item["dst"] for item in result["trans_result"]]
                return "\n".join(translations)
            else:
                return f"翻译失败: {result.get('error_msg', '未知错误')}"

        except Exception as e:
            return f"翻译失败: {str(e)}"

    def _translate_free(self, text, from_lang="auto", to_lang="zh"):
        try:
            import urllib.request
            import urllib.parse
            import json

            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": from_lang if from_lang != "auto" else "auto",
                "tl": to_lang,
                "dt": "t",
                "q": text,
            }

            full_url = url + "?" + urllib.parse.urlencode(params)
            req = urllib.request.Request(full_url)
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )

            response = urllib.request.urlopen(req, timeout=15)
            result = json.loads(response.read().decode("utf-8"))

            if result and result[0]:
                translations = [item[0] for item in result[0] if item[0]]
                return "".join(translations)
            else:
                return "翻译失败: 无法解析结果"

        except Exception as e:
            return f"翻译失败: {str(e)}\n\n请检查网络连接，或配置百度翻译API密钥。"

    def translate(self, text, from_lang="auto", to_lang="zh", engine="free"):
        if not text or not text.strip():
            return "没有可翻译的文本"

        if engine == "baidu":
            return self.translate_baidu(text, from_lang, to_lang)
        else:
            return self._translate_free(text, from_lang, to_lang)

    def ocr_and_translate(self, image_path, from_lang="auto", to_lang="zh"):
        try:
            try:
                import pytesseract
                from PIL import Image

                image = Image.open(image_path)
                text = pytesseract.image_to_string(image)
                if text.strip():
                    translation = self.translate(text, from_lang, to_lang)
                    return f"识别文本:\n{text}\n\n翻译结果:\n{translation}"
                else:
                    return "未能识别到文字内容"
            except ImportError:
                return (
                    "OCR功能需要安装 pytesseract 和 Pillow 库。\n\n"
                    "请运行: pip install pytesseract pillow\n\n"
                    "同时需要安装 Tesseract OCR 引擎。"
                )
        except Exception as e:
            return f"OCR失败: {str(e)}"
