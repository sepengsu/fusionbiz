from config.config_manager import load_config

def build_prompt_from_config(question: str, chunks: list) -> dict:
    """
    config.json을 바탕으로 system_prompt, user_prompt_template, model, temperature 등을 불러와
    ChatCompletion 호출용 prompt dictionary를 구성함
    """
    config = load_config()

    system_prompt = config.get("system_prompt", "AI 어시스턴트입니다.")
    user_template = config.get("user_prompt_template", "문서:\n{context}\n\n질문: {query}\n답변:")
    model_name = config.get("llm_model", "gpt-4o")
    temperature = config.get("temperature", 0.4)

    context = "\n\n".join(chunk["text"] for chunk in chunks)
    user_prompt = user_template.replace("{context}", context).replace("{query}", question)

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "model": model_name,
        "temperature": temperature
    }
