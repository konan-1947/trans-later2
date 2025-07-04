# app/core/translation_service.py
import google.generativeai as genai
import json
from app.config.settings import GEMINI_API_KEY


class TranslationService:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def translate_page_json(self, lines_to_translate, domain="Information Technology", audience="professionals"):
        if not lines_to_translate:
            return {}

        # Tạo đối tượng JSON đầu vào
        input_json_obj = {f"line_{i}": text for i,
                          text in enumerate(lines_to_translate)}
        input_json_str = json.dumps(
            input_json_obj, indent=2, ensure_ascii=False)

        prompt_template = """
---INSTRUCTION---
You are an expert JSON-based translation API. Your task is to translate the text content of each line from a document page, from English to Vietnamese.
You specialize in the field of {domain} and the translation should be suitable for {audience}.

Follow these rules STRICTLY:
1.  The input is a JSON object where keys are line IDs and values are the original English text.
2.  Your output MUST be a single, valid JSON object and nothing else.
3.  The output JSON object MUST have the exact same keys as the input. The values must be the translated Vietnamese text.
4.  Maintain a formal, professional, and precise tone. Prioritize technical accuracy.
5.  Keep proper nouns like "Docker", "MacOS", "Windows" in their original form.

---EXAMPLE---
Input JSON:
{{
  "line_0": "1. What is Docker?",
  "line_1": "When developing application, it usually needs belonging dependencies"
}}

Output JSON:
{{
  "line_0": "1. Docker là gì?",
  "line_1": "Khi phát triển ứng dụng, nó thường cần các phần phụ thuộc đi kèm"
}}
---END EXAMPLE---

---INPUT JSON TO TRANSLATE---
{input_json}

---OUTPUT JSON---
"""
        prompt = prompt_template.format(
            domain=domain,
            audience=audience,
            input_json=input_json_str
        )

        try:
            response = self.model.generate_content(prompt)
            # Dọn dẹp output của AI, chỉ lấy phần JSON
            clean_response = response.text.strip().replace(
                "```json", "").replace("```", "").strip()

            # Phân tích cú pháp JSON trả về
            translated_json_obj = json.loads(clean_response)
            return translated_json_obj

        except Exception as e:
            print(f"Error processing Gemini JSON response: {e}")
            # Trả về một đối tượng rỗng nếu có lỗi để không làm crash app
            return {}
