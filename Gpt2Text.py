import json


def extract_content_with_roles(file_path):
    """
    從指定的 JSON 檔案中讀取資料，提取所有 'parts' 欄位及其對應的 'author' 中的 'role'。

    Args:
        file_path (str): JSON 檔案的路徑。

    Returns:
        list: 一個包含字典的列表，每個字典包含 'role' 和 'content'。
              如果檔案不存在或格式錯誤，則返回空列表。
    """
    extracted_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'mapping' in data and isinstance(data['mapping'], dict):
            for key, value in data['mapping'].items():
                if isinstance(value, dict):
                    message = value.get('message')
                    if isinstance(message, dict):
                        author = message.get('author')
                        content = message.get('content')

                        role = None
                        if isinstance(author, dict):
                            role = author.get('role')
                            if role == "assistant":
                                role = "chatgpt"  # 将 "assistant" 改为 "chatgpt"

                        parts = None
                        if isinstance(content, dict):
                            parts = content.get('parts')

                        # 如果 'parts' 存在且是列表，并且 role 也存在
                        if isinstance(parts, list) and role is not None:
                            full_content = "\n".join(str(p) for p in parts)

                            # 优化1: 当 role 为 "system" 且 content 为空时，不写入
                            if role == "system" and not full_content.strip():
                                continue  # 跳过当前循环，不添加到 extracted_data

                            extracted_data.append({
                                'role': role,
                                'content': full_content
                            })

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'")
    except json.JSONDecodeError:
        print(f"錯誤：檔案 '{file_path}' 不是有效的 JSON 格式。")
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")

    return extracted_data


def save_formatted_text_to_file(data, output_file_path):
    """
    將包含 'role' 和 'content' 的數據以格式化的純文字形式寫入檔案。

    Args:
        data (list): 包含字典的列表，每個字典包含 'role' 和 'content'。
        output_file_path (str): 輸出的檔案路徑。
    """
    user_count = 0  # 初始化用户角色计数器
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for item in data:
                role_label = item.get('role', 'Unknown')
                content = item.get('content', '')

                # 优化2: 当 role 为 "user" 时，前面多加一个换行并添加编号
                if role_label == "user":
                    user_count += 1  # 用户计数器递增
                    f.write("\n")  # 在用户内容前多加一个换行
                    # 写入带有编号的角色信息
                    f.write(f"--- {user_count}、{role_label.upper()} ---\n")
                else:
                    # 对于非用户角色，正常写入角色信息
                    f.write(f"--- {role_label.upper()} ---\n")

                # 写入内容
                f.write(content)
                # 在每个条目之间添加一些空行以提高可读性
                f.write("\n\n")
        print(f"成功將格式化後的內容寫入到檔案 '{output_file_path}'")
    except Exception as e:
        print(f"寫入檔案時發生錯誤：{e}")


def main():
    """
    主函數，執行腳本。
    """
    json_file = '提取内容.json'
    output_file = 'output.txt'  # 始终使用 output.txt

    extracted_data = extract_content_with_roles(json_file)

    if extracted_data:
        save_formatted_text_to_file(extracted_data, output_file)
    else:
        print("未能在檔案中提取到任何內容。")


if __name__ == '__main__':
    main()