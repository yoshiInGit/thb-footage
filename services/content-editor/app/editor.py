import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from shared.gemini import GeminiClient

# AIからの出力を構造化するためのPydanticモデル定義
class PatchItem(BaseModel):
    search: str = Field(
        description="置換対象となる元のテキスト。ファイル内で一意に特定できるよう、前後の行を含めるなど十分な長さを指定してください。"
    )
    replace: str = Field(
        description="置換後のテキスト。元のテキスト(search)と置き換える内容を指定します。"
    )

class PatchList(BaseModel):
    patches: List[PatchItem] = Field(
        description="適用する差分（パッチ）のリスト。"
    )

def generate_patch(
    content: str,
    task: str,
    references: List[Dict[str, str]],
    model_name: str = "gemini-2.5-flash",
    log_dir: str = "output/logs"
) -> List[Dict[str, str]]:
    """
    Gemini APIを呼び出して、content.txtに対する差分（パッチ）データを生成する。
    
    :param content: 編集対象のcontent.txtの中身
    :param task: ユーザーの指示（task.txt）
    :param references: 参考資料のリスト。各要素は {"name": "ファイル名", "content": "中身"} の辞書
    :param model_name: 使用するモデル名
    :param log_dir: ログ出力先
    :return: 差分データのリスト [{"search": "...", "replace": "..."}, ...]
    """
    
    # 参考資料のフォーマット化
    ref_section = ""
    if references:
        ref_section += "## 参考資料 (References)\n"
        for ref in references:
            ref_section += f"### ファイル: {ref['name']}\n"
            ref_section += f"```\n{ref['content']}\n```\n\n"
    else:
        ref_section += "## 参考資料: なし\n"

    # プロンプトの組み立て
    prompt = f"""あなたはテキスト編集のアシスタントです。
提供された「現在のコンテンツ」に対して、「指示(task)」および「参考資料」を基に編集を行い、差分（パッチ）データを生成してください。

### 置換ルールと注意点：
1. 出力は指定されたJSONスキーマに従う必要があります。
2. 各パッチの `search` フィールドには、置換対象となる文字列を正確に指定してください。
3. `search` に指定する文字列は、現在のコンテンツ内で **一意に特定できる十分な長さ（前後の行を含めるなど）** にしてください。部分的に重複する短いワードだけを指定すると、意図しない場所が置換されたり、エラーになったりします。
4. インデントや改行（`\\n`）も正確に一致させる必要があります。

---

## 現在のコンテンツ (Current Content)
```
{content}
```

## 指示 (Task)
{task}

{ref_section}
"""

    # GeminiClientの初期化と呼び出し
    # 構造化出力のために response_mime_type と response_schema を指定する
    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": PatchList,
        "temperature": 0.2, # 決定論的な出力を高めるために低めに設定
    }
    
    client = GeminiClient(
        model_name=model_name,
        log_dir=log_dir,
        generation_config=generation_config
    )
    
    print("[editor] Calling Gemini to generate patches...")
    response_text = client.generate_content(prompt)
    
    try:
        response_data = json.loads(response_text)
        # Pydanticモデルでパースされた patches リストを取得して辞書のリストに変換
        patches = response_data.get("patches", [])
        return [{"search": p["search"], "replace": p["replace"]} for p in patches]
    except Exception as e:
        print(f"[editor] Failed to parse Gemini response as JSON: {e}")
        print(f"[editor] Raw Response: {response_text}")
        raise e
