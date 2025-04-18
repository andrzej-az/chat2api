import asyncio
import json
from typing import AsyncGenerator


async def transform_delta_stream(input_stream) -> AsyncGenerator[str, None]:
    current_message = None
    current_event = None

    async for line in input_stream:
        line = line.decode("utf-8").strip()
        if not line:
            continue

            # 处理事件类型行
        if line.startswith("event: "):
            current_event = line[7:]
            continue

            # 处理数据行
        if line.startswith("data: "):
            data = line[6:]

            # 处理特殊结束标记 [DONE]，直接原样返回
            if data == "[DONE]":
                yield line
                continue

            try:
                json_data = json.loads(data)

                # 1. 处理完整的消息数据
                if "message" in json_data:
                    current_message = json_data["message"]
                    yield f'data: {json.dumps({"message": current_message})}'
                    continue

                # 2. 处理delta编码的消息
                if current_event == "delta":
                    # 2.1 处理包含完整消息的v字段
                    if "v" in json_data and isinstance(json_data["v"], dict) and "message" in json_data["v"]:
                        current_message = json_data["v"]["message"]
                        yield f'data: {json.dumps({"message": current_message})}'
                        continue

                    # 2.2 处理简单的文本增量 {"v": "text"}
                    if "v" in json_data and isinstance(json_data["v"], str):
                        if current_message is None:
                            current_message = {
                                "content": {
                                    "content_type": "text",
                                    "parts": [""]
                                }
                            }
                        # 确保content和parts结构存在
                        if "content" not in current_message:
                            current_message["content"] = {"content_type": "text", "parts": [""]}
                        if "parts" not in current_message["content"]:
                            current_message["content"]["parts"] = [""]
                        if not current_message["content"]["parts"]:
                            current_message["content"]["parts"].append("")
                        # 追加文本到第一个part
                        current_message["content"]["parts"][0] += json_data["v"]
                        yield f'data: {json.dumps({"message": current_message})}'
                        continue

                    # 2.3 处理patch操作
                    if "p" in json_data and "o" in json_data:
                        if current_message is None:
                            current_message = {}
                        current_message = apply_patch(current_message, json_data)
                        yield f'data: {json.dumps({"message": current_message})}'
                        continue

                # 3. 不是delta事件的数据，直接输出
                if isinstance(json_data, dict) and "v" in json_data and isinstance(json_data["v"],
                                                                                   dict) and "message" in json_data[
                    "v"]:
                    yield f'data: {json.dumps({"message": json_data["v"]["message"]})}'
                else:
                    # 其他情况直接原样返回
                    yield line

            except json.JSONDecodeError:
                # 处理简单的字符串数据（如"v1"），直接返回原行
                yield line

            # 输出最后的消息（如果有）
        if current_message is not None:
            yield f'data: {json.dumps({"message": current_message})}'


def apply_patch(message: dict, patch: dict) -> dict:
    """应用单个patch操作到消息"""
    path = patch["p"]
    operation = patch["o"]
    value = patch.get("v", None)

    # 处理根路径
    if path == "":
        if operation == "add":
            return value
        elif operation == "patch":
            for sub_patch in value:
                message = apply_patch(message, sub_patch)
            return message
        return message

    # 分割路径
    parts = [p for p in path.split("/") if p]
    target = message

    # 导航到目标位置
    for part in parts[:-1]:
        if part not in target:
            target[part] = {}
        target = target[part]

    last_part = parts[-1]

    # 应用操作
    if operation == "replace":
        target[last_part] = value
    elif operation == "append":
        if last_part not in target:
            target[last_part] = []
        if isinstance(target[last_part], list):
            target[last_part].append(value)
        elif isinstance(target[last_part], str):
            target[last_part] += str(value)
    elif operation == "truncate":
        if isinstance(target[last_part], (list, str)):
            target[last_part] = target[last_part][:value]
    elif operation == "add":
        target[last_part] = value
    elif operation == "remove":
        if last_part in target:
            del target[last_part]

    return message


async def main():
    # 模拟输入流
    input_stream = [
        'event: delta_encoding',
        'data: "v1"',
        '',
        'event: delta',
        'data: {"p": "", "o": "add", "v": {"message": {"id": "1471f310-cd55-4f98-be10-a8a0ab0cf19e", "author": {"role": "system", "name": null, "metadata": {}}, "create_time": null, "update_time": null, "content": {"content_type": "text", "parts": [""]}, "status": "finished_successfully", "end_turn": true, "weight": 0.0, "metadata": {"is_visually_hidden_from_conversation": true}, "recipient": "all", "channel": null}, "conversation_id": "680225d7-a0d8-8004-aaba-00083cfb2ae3", "error": null}, "c": 0}',
        '',
        'event: delta',
        'data: {"v": {"message": {"id": "906d0092-95ba-4517-a3ef-081d64a86a88", "author": {"role": "user", "name": null, "metadata": {}}, "create_time": 1744971224.028, "update_time": null, "content": {"content_type": "text", "parts": ["\u753b\u4e00\u53ea\u732b"]}, "status": "finished_successfully", "end_turn": null, "weight": 1.0, "metadata": {"serialization_metadata": {"custom_symbol_offsets": []}, "request_id": "9323641f7a5008e0-SJC", "message_source": null, "timestamp_": "absolute", "message_type": null}, "recipient": "all", "channel": null}, "conversation_id": "680225d7-a0d8-8004-aaba-00083cfb2ae3", "error": null}, "c": 1}',
        '',
        'data: {"v": {"message": {"id": "02e534af-11f5-4e74-ac37-71f65e845332", "author": {"role": "assistant", "name": null, "metadata": {}}, "create_time": 1744971224.343261, "update_time": null, "content": {"content_type": "text", "parts": [""]}, "status": "in_progress", "end_turn": null, "weight": 1.0, "metadata": {"citations": [], "content_references": [], "message_type": "next", "model_slug": "gpt-4o", "default_model_slug": "auto", "parent_id": "906d0092-95ba-4517-a3ef-081d64a86a88", "model_switcher_deny": [{"slug": "o1-mini", "context": "regenerate", "reason": "unsupported_tool_use", "is_available": false, "description": "\u6b64\u6a21\u578b\u4e0d\u652f\u6301\u4f7f\u7528\u5de5\u5177\u3002"}, {"slug": "o1-mini", "context": "conversation", "reason": "unsupported_tool_use", "is_available": false, "description": "\u6b64\u6a21\u578b\u4e0d\u652f\u6301\u4f7f\u7528\u5de5\u5177\u3002"}]}, "recipient": "t2uay3k.sj1i4kz", "channel": null}, "conversation_id": "680225d7-a0d8-8004-aaba-00083cfb2ae3", "error": null}, "c": 2}',
        '',
        'data: [DONE]'
    ]
    # 处理并输出转换后的流
    async for complete_json in transform_delta_stream(input_stream):
        print(complete_json)


if __name__ == "__main__":
    asyncio.run(main())
