import json
import os  # 导入 os 模块用于文件系统操作


def extract_content_with_roles(file_path):
    """
    從指定的 JSON 檔案中讀取資料，提取所有 'parts' 欄位及其對應的 'author' 中的 'role'。
    同時也提取 role 為 'tool' 的內容，並將其與主內容分開返回。

    Args:
        file_path (str): JSON 檔案的路徑。

    Returns:
        tuple: 包含兩個列表的元組。
               第一個列表是主內容 (role, content)，
               第二個列表是工具內容 (role, content)。
               如果檔案不存在或格式錯誤，則返回空列表的元組。
    """
    extracted_main_data = []
    extracted_tool_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'mapping' in data and isinstance(data['mapping'], dict):
            for key, value in data['mapping'].items():
                if isinstance(value, dict):
                    message = value.get('message')
                    if isinstance(message, dict):
                        author = message.get('author')
                        content_obj = message.get('content')  # 重命名以避免与下面的 content 变量冲突

                        role = None
                        if isinstance(author, dict):
                            role = author.get('role')
                            if role == "assistant":
                                role = "chatgpt"  # 将 "assistant" 改为 "chatgpt"

                        full_content = ""
                        # 检查 content_obj 是否是字典，以及是否有 parts 键
                        if isinstance(content_obj, dict):
                            if 'parts' in content_obj and isinstance(content_obj['parts'], list):
                                parts = content_obj['parts']
                                full_content = "\n".join(str(p) for p in parts)
                            elif content_obj.get('content_type') in ['thoughts', 'reasoning_recap']:
                                # 对于 content_type 为 'thoughts' 或 'reasoning_recap' 的情况，直接取 content 字段
                                full_content = content_obj.get('content', '')

                        # 如果角色存在
                        if role is not None:
                            # 过滤空的 System 和 Assistant/ChatGPT 内容
                            # 如果 role 是 "system" 或 "chatgpt" 且内容为空白，则跳过
                            if (role == "system" or role == "chatgpt") and not full_content.strip():
                                continue  # 跳过当前循环，不添加到 extracted_data

                            if role == "tool":
                                # 如果是 tool 角色且有内容，添加到工具内容列表
                                if full_content.strip():  # 确保 tool 内容不为空
                                    extracted_tool_data.append({
                                        'role': role,
                                        'content': full_content
                                    })
                                # tool 内容不写入主文件，所以这里不添加到 extracted_main_data
                            else:
                                # 其他角色（user, chatgpt, system）添加到主内容列表
                                extracted_main_data.append({
                                    'role': role,
                                    'content': full_content
                                })

    except FileNotFoundError:
        raise  # 重新抛出异常，让上层函数处理
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 格式错误: {e}")
    except Exception as e:
        raise Exception(f"提取内容时发生未预期错误: {e}")

    return extracted_main_data, extracted_tool_data


def save_formatted_text_to_main_file(data, output_file_path):
    """
    將包含 'role' 和 'content' 的數據以格式化的純文字形式寫入檔案。
    用於保存主對話內容到对应文件名的txt中。

    Args:
        data (list): 包含字典的列表，每個字典包含 'role' 和 'content'。
        output_file_path (str): 輸出的檔案路徑。
    """
    user_count = 0  # 初始化用户角色计数器
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_file_path, 'w', encoding='utf-8') as f:  # 注意这里是 'w' 模式，每个JSON对应一个新文件
            for item in data:
                role_label = item.get('role', 'Unknown')
                content = item.get('content', '')

                # 当 role 为 "user" 时，前面多加一个换行并添加编号
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
        print(f"成功將主對話內容寫入到檔案 '{output_file_path}'")
    except Exception as e:
        raise Exception(f"寫入主對話檔案時發生錯誤：{e}")


def save_tool_content_to_separate_file(tool_data, base_filename, output_directory):
    """
    將提取到的 tool 內容以純文字格式寫入一個獨立的檔案。

    Args:
        tool_data (list): 包含 tool 內容的列表。
        base_filename (str): 原json文件名 (不带扩展名)。
        output_directory (str): 输出目录。
    """
    if not tool_data:
        return  # 如果没有 tool 内容则直接返回，并且不再打印日志

    output_file_name = f"{base_filename}_附件内容.txt"
    output_full_path = os.path.join(output_directory, output_file_name)

    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_full_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_full_path, 'w', encoding='utf-8') as f:  # 'w' 模式，为每个 JSON 的 tool 内容创建新文件
            for item in tool_data:
                f.write(f"--- TOOL ---\n")
                f.write(item.get('content', ''))
                f.write("\n\n")  # 每个 tool 内容块之间也用空行分隔
        print(f"成功將工具內容寫入到檔案 '{output_full_path}'")
    except Exception as e:
        print(f"寫入工具檔案時發生錯誤：{e}")


def main():
    """
    主函數，遍歷當前目錄及其所有子目錄下的所有 JSON 檔案，處理並保存到 'result' 目錄。
    輸出目錄結構與源目錄結構保持一致。
    """
    current_root_directory = os.getcwd()  # 获取当前脚本运行的根目录
    base_output_directory = os.path.join(current_root_directory, '../result')  # 定义结果输出的根目录

    # 遍历当前根目录及其所有子目录
    for root, dirs, files in os.walk(current_root_directory):
        # 排除 result 目录本身，避免无限递归或尝试处理已生成的文件
        if 'result' in dirs:
            dirs.remove('result')  # 这会防止 os.walk 进入 'result' 目录

        for filename in files:
            if filename.endswith('.json'):
                json_file_path = os.path.join(root, filename)

                # 计算相对于 current_root_directory 的路径
                # 例如：如果 json_file_path 是 D:/Scripts/folder/test.json
                # current_root_directory 是 D:/Scripts
                # relative_path 就是 folder/test.json
                relative_path = os.path.relpath(json_file_path, current_root_directory)

                # 构建输出文件的相对路径（在 result 目录下的对应路径）
                # 例如：如果 relative_path 是 folder/test.json
                # base_output_directory 是 D:/Scripts/result
                # output_full_path_base_no_ext 就是 D:/Scripts/result/folder/test
                output_full_path_base_no_ext = os.path.join(base_output_directory, os.path.splitext(relative_path)[0])

                # 确保输出文件的目录结构在 result 目录下也存在
                output_dir_for_current_file = os.path.dirname(output_full_path_base_no_ext)
                if not os.path.exists(output_dir_for_current_file):
                    os.makedirs(output_dir_for_current_file)

                # 主对话内容的输出文件路径
                output_main_txt_file_path = f"{output_full_path_base_no_ext}.txt"

                # 获取不带扩展名的文件名，用于生成 _附件内容.txt
                base_filename_no_ext = os.path.splitext(filename)[0]

                print(f"\n正在处理文件: {json_file_path}...")
                try:
                    extracted_main_data, extracted_tool_data = extract_content_with_roles(json_file_path)

                    # 处理主内容
                    if extracted_main_data:
                        save_formatted_text_to_main_file(extracted_main_data, output_main_txt_file_path)
                    else:
                        print(f"未能在文件 '{json_file_path}' 中提取到任何有效主内容。")

                    # 处理工具内容
                    if extracted_tool_data:
                        # 对于工具内容，其输出目录需要与主文件在 result 目录下的子目录保持一致
                        # output_dir_for_current_file 就是这个子目录
                        save_tool_content_to_separate_file(extracted_tool_data, base_filename_no_ext,
                                                           output_dir_for_current_file)

                except FileNotFoundError:
                    print(f"错误: 找不到文件 '{json_file_path}'，跳过。")
                except ValueError as ve:
                    print(f"错误: 文件 '{json_file_path}' JSON 格式异常: {ve}，跳过。")
                except Exception as e:
                    print(f"处理文件 '{json_file_path}' 时发生未预期错误: {e}，跳过。")


if __name__ == '__main__':
    main()