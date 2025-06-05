import os
import re

def transform_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) % 2 != 0:
        raise ValueError(f"文件 {input_path} 格式错误：数据行数应为偶数，每个号码对应一个 token ")

    result_lines = []
    for i in range(0, len(lines), 2):
        phone = lines[i]
        token = lines[i + 1]
        formatted = f"{token}#{phone}#00"
        result_lines.append(formatted)

    # 用换行拼接
    final_output = "\n".join(result_lines)

    with open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(final_output)

def process_all_phone_files():
    current_dir = os.getcwd()
    for filename in os.listdir(current_dir):
        if filename.startswith("phone") and filename.endswith(".txt"):
            # 提取 "phone" 后面的部分作为后缀
            suffix = re.sub(r'^phone', '', filename)
            suffix = re.sub(r'\.txt$', '', suffix)
            input_path = os.path.join(current_dir, filename)
            output_filename = f"output{suffix}.txt"
            output_path = os.path.join(current_dir, output_filename)
            print(f"✅ 正在处理：{filename} → {output_filename}")
            try:
                transform_file(input_path, output_path)
            except Exception as e:
                print(f"❌ 错误处理 {filename}：{e}")

# 执行处理
process_all_phone_files()
