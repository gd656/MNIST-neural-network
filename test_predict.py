import requests

# 修改成你的图片路径
image_path = r"C:\Users\PC\Desktop\7.png"

with open(image_path, "rb") as f:

    response = requests.post(
        "http://127.0.0.1:5000/api/predict",
        files={
            "image": f
        }
    )

print("HTTP状态码：", response.status_code)
print("后端返回：")
print(response.json())