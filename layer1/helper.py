import os
import re
from typing import List, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam


class AgentsLLM:
    def __init__(self, model: Optional[str] = None, apiKey: Optional[str] = None,
                 baseUrl: Optional[str] = None, timeout: Optional[int] = None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or 60

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("Please define your variables first")

        self.client = AsyncOpenAI(
            api_key=apiKey, base_url=baseUrl, timeout=self.timeout)

    async def think(self, messages: List[ChatCompletionMessageParam], temperature: float = 0) -> str:
        current_model = self.model
        assert current_model is not None
        try:
            response = await self.client.chat.completions.create(
                model=current_model,
                messages=messages,
                temperature=temperature,
                max_tokens=10
            )
            content = response.choices[0].message.content
            return str(content).strip() if content else ""
        except Exception as e:
            return f"ERROR: {e}"

    def parse_sentiment(self, raw_result: str) -> int:
        cleaned = raw_result.strip() if raw_result is not None else ""
        if cleaned in {"-1", "0", "1"}:
            return int(cleaned)
        match = re.fullmatch(r"(-1|0|1)", cleaned)
        if match:
            return int(match.group(1))
        return 999  # Error code


async def agent_process(prompt, llm, index, content, sem):
    '''
    param content: sentence to be rated
    param sem: semaphore
    '''
    async with sem:
        messages = [{"role": "user", "content": prompt.format(text=content)}]
        raw_res = await llm.think(messages)
    score = llm.parse_sentiment(raw_res)
    # Debug: inspect model output vs parsed score
#     print(f"[DEBUG] index={index}, raw_res={raw_res!r}, parsed_sentiment={score}\n")
    return {"index": index, "sentiment": score}
