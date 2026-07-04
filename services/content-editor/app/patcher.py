import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def apply_patches(content: str, patches: List[Dict[str, str]], strict: bool = True) -> str:
    """
    差分データ（パッチ）をテキストコンテンツに適用する。
    
    :param content: 元のテキストコンテンツ
    :param patches: 差分データのリスト。各要素は {"search": "...", "replace": "..."} の辞書
    :param strict: True の場合、search文字列が見つからない、または複数見つかった場合にエラーをスローする
    :return: 置換適用後のテキストコンテンツ
    """
    current_content = content
    
    for i, patch in enumerate(patches):
        search_str = patch.get("search")
        replace_str = patch.get("replace")
        
        if search_str is None or replace_str is None:
            raise ValueError(f"パッチインデックス {i} が不正です。'search' と 'replace' キーが必要です。")
            
        # search文字列の出現回数をカウント
        count = current_content.count(search_str)
        
        if count == 0:
            msg = f"置換対象の文字列が見つかりませんでした (インデックス {i}):\n--- SEARCH ---\n{search_str}\n--------------"
            if strict:
                raise ValueError(msg)
            else:
                logger.warning(msg)
                continue
        elif count > 1:
            msg = f"置換対象の文字列が複数見つかりました。一意に特定できません (インデックス {i}, 出現回数: {count}):\n--- SEARCH ---\n{search_str}\n--------------"
            if strict:
                raise ValueError(msg)
            else:
                logger.warning(msg)
                # strictではない場合は、すべて置換してしまうか、スキップするか？
                # ここでは安全のためにスキップします。
                continue
                
        # 1箇所だけ見つかったので置換を実行
        current_content = current_content.replace(search_str, replace_str, 1)
        logger.info(f"パッチ適用成功 (インデックス {i})")
        
    return current_content
