import json

def extract_parts_from_json(file_path):
    """
    從指定的 JSON 檔案中讀取資料，並提取所有 'parts' 欄位。

    Args:
        file_path (str): JSON 檔案的路徑。

    Returns:
        list: 一個包含所有提取到的 'parts' 內容的列表。
              如果檔案不存在或格式錯誤，則返回空列表。
    """
    all_parts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 檢查 'mapping' 鍵是否存在且為字典
        if 'mapping' in data and isinstance(data['mapping'], dict):
            # 遍歷 'mapping' 中的每一個物件
            for key, value in data['mapping'].items():
                # 使用 .get() 來安全地訪問巢狀的鍵，避免因鍵不存在而出錯
                if isinstance(value, dict):
                    message = value.get('message')
                    if isinstance(message, dict):
                        content = message.get('content')
                        if isinstance(content, dict):
                            parts = content.get('parts')
                            # 如果 'parts' 存在且是列表，則將其內容添加到結果列表中
                            if isinstance(parts, list):
                                all_parts.extend(parts)

    except FileNotFoundError:
        print(f"錯誤：找不到檔案 '{file_path}'")
    except json.JSONDecodeError:
        print(f"錯誤：檔案 '{file_path}' 不是有效的 JSON 格式。")
    except Exception as e:
        print(f"發生未預期的錯誤：{e}")

    return all_parts

def save_parts_to_file(parts_data, output_file_path):
    """
    將提取到的 parts 內容以 JSON 格式寫入一個檔案。

    Args:
        parts_data (list): 包含 parts 內容的列表。
        output_file_path (str): 輸出的檔案路徑。
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 使用 json.dump 來美化輸出並寫入檔案
            json.dump(parts_data, f, indent=2, ensure_ascii=False)
        print(f"成功將提取的內容寫入到檔案 '{output_file_path}'")
    except Exception as e:
        print(f"寫入檔案時發生錯誤：{e}")

def main():
    """
    主函數，執行腳本。
    """
    # 將 '運行JS项目指南.json' 替換為您的實際檔案名
    json_file = '尼日利亚订阅问题.json'
    # 定義輸出的檔案名
    output_file = 'extracted_parts_output.json'

    extracted_parts = extract_parts_from_json(json_file)

    if extracted_parts:
        save_parts_to_file(extracted_parts, output_file)
    else:
        print("未能在檔案中提取到任何 'parts' 內容。")

if __name__ == '__main__':
    main()
