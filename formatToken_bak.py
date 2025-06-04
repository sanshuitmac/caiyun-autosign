def transform_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) % 2 != 0:
        raise ValueError("文件格式错误：数据行数应为偶数，每个号码对应一个 token")

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for i in range(0, len(lines), 2):
            phone = lines[i]
            token = lines[i + 1]
            formatted_line = f"{token}#{phone}#00"
            f_out.write(formatted_line + '\n')


# 示例用法
transform_file('phones.txt', 'output.txt')
