import json
import os

def merge_json_files(folder_path, output_file):
    merged_data = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                temp_data = []
                for item in data:
                    if isinstance(item['answers'], list):
                        if len(item['answers']) == 0:
                            continue
                        answer = item['answers'][0]
                        if answer == item['question'] and len(item['answers']) > 1:
                            answer = item['answers'][1]
                        random_data = {'question': item['question'], 'answers': answer}
                        temp_data.append(random_data)
                        continue
                    temp_data.append(item)
                merged_data.extend(temp_data)
    print(f'合并了 {len(merged_data)} 条数据')
    # 将合并后的数据写入一个新的 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

# 示例用法
folder_path = './results'  # 替换为你的文件夹路径
output_file = 'merged_output.json'  # 合并后的输出文件名
merge_json_files(folder_path, output_file)
