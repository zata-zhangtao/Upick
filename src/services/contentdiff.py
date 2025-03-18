from difflib import SequenceMatcher
from typing import Tuple, List,Literal
from src.log import get_logger
logger = get_logger("services.contentdiff")

# Define the allowed tag literals
TagType = Literal["replace", "delete", "insert"]
def get_content_diff(old_content:str, new_content:str,return_tags:List[TagType]=["insert"])->Tuple[float, List[str]]:
    """
    Compare old and new content to find differences.
    Returns a similarity ratio and the differences.

    Args:
        old_content (str): The old content to compare.
        new_content (str): The new content to compare.
        return_tags (List[str]): The tags to return.
    Returns:
        Tuple[float, List[str]]: A tuple containing the similarity ratio and the differences.
    """
    # Calculate similarity ratio
    matcher = SequenceMatcher(None, old_content, new_content)
    similarity = matcher.ratio()

    

    # Get differences
    diffs = []
    diff_details = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            if tag in return_tags:
                if tag == 'replace':
                    diffs.append(f"Changed: '{old_content[i1:i2]}' -> '{new_content[j1:j2]}'")
                elif tag == 'delete':
                    diffs.append(f"Deleted: '{old_content[i1:i2]}'")
                elif tag == 'insert':
                    diffs.append(f"Added: '{new_content[j1:j2]}'")
                diff_details.append(f"{tag}: '{old_content[i1:i2]}' -> '{new_content[j1:j2]}'")
    logger.debug(f"差异详情: {diff_details}")

    return similarity, diffs

def has_significant_changes(old_content, new_content, threshold=0.95):
    """
    Determine if content changes are significant based on similarity threshold.
    Returns True if changes are significant, False otherwise.
    """
    similarity, _ = get_content_diff(old_content, new_content)
    return similarity < threshold



if __name__ == "__main__":
    old_content = "你好，世界！"
    new_content = "你好，世界！你好，宇宙！"
    similarity, diffs = get_content_diff(old_content, new_content)
    # print(f"相似度: {similarity}")
    # print(f"差异: {diffs}")

