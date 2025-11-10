import json

json_file = r"D:\MLE\Homework2-Submission\arxiv_clean.json"

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# 打印前几个条目，看看里面的字段
for i, paper in enumerate(data[:3]):
    print(json.dumps(paper, indent=2, ensure_ascii=False))
