from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageOps
import numpy as np

from neural_network import network


app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    return "MNIST 识别后端运行成功！"


def preprocess_image(image):
    """
    将用户上传的图片处理成接近 MNIST 格式的 28×28 图片
    """

    # 1. 转灰度
    image = image.convert("L")

    # 2. 判断背景颜色
    image_array = np.asarray(image)

    corner_pixels = np.array([
        image_array[0, 0],
        image_array[0, -1],
        image_array[-1, 0],
        image_array[-1, -1]
    ])

    background_value = np.mean(corner_pixels)

    # 白色背景 + 黑色数字 → 反色
    if background_value > 127:
        image = ImageOps.invert(image)

    # 3. 增强对比度
    image = ImageOps.autocontrast(image)

    image_array = np.asarray(image)

    # 4. 找到数字区域
    mask = image_array > 30

    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]

    if len(rows) == 0 or len(cols) == 0:
        raise ValueError("没有检测到有效的数字，请重新上传图片")

    top = rows[0]
    bottom = rows[-1] + 1
    left = cols[0]
    right = cols[-1] + 1

    # 5. 裁剪数字
    image = image.crop(
        (left, top, right, bottom)
    )

    width, height = image.size

    # 6. 缩放到 20×20 范围
    scale = 20 / max(width, height)

    new_width = max(1, int(width * scale))
    new_height = max(1, int(height * scale))

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    # 7. 再次增强亮度
    image = ImageOps.autocontrast(image)

    # 8. 创建 28×28 黑色画布
    canvas = Image.new(
        "L",
        (28, 28),
        0
    )

    # 9. 先放到几何中心
    paste_x = (28 - new_width) // 2
    paste_y = (28 - new_height) // 2

    canvas.paste(
        image,
        (paste_x, paste_y)
    )

    # ==================================================
    # 10. 根据像素重心重新调整数字位置
    # ==================================================

    canvas_array = np.asarray(
        canvas,
        dtype=np.float64
    )

    total = canvas_array.sum()

    if total > 0:

        y_indices, x_indices = np.indices(
            canvas_array.shape
        )

        center_x = (
            (x_indices * canvas_array).sum()
            / total
        )

        center_y = (
            (y_indices * canvas_array).sum()
            / total
        )

        # MNIST 中心大约在 13.5, 13.5
        target_x = 13.5
        target_y = 13.5

        shift_x = int(round(
            target_x - center_x
        ))

        shift_y = int(round(
            target_y - center_y
        ))

        # 使用新的画布进行平移
        shifted = np.zeros(
            (28, 28),
            dtype=np.uint8
        )

        for y in range(28):

            for x in range(28):

                new_x = x + shift_x
                new_y = y + shift_y

                if (
                    0 <= new_x < 28
                    and 0 <= new_y < 28
                ):
                    shifted[
                        new_y,
                        new_x
                    ] = int(canvas_array[y, x])

        canvas = Image.fromarray(
            shifted
        )

    # ==================================================
    # 11. 最后重新拉伸亮度
    # ==================================================

    canvas_array = np.asarray(
        canvas,
        dtype=np.float64
    )

    max_value = canvas_array.max()

    if max_value > 0:

        canvas_array = (
            canvas_array / max_value * 255
        )

        canvas = Image.fromarray(
            canvas_array.astype(np.uint8)
        )

    return canvas


@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        # ==============================
        # 1. 检查图片
        # ==============================
        if "image" not in request.files:

            return jsonify({
                "success": False,
                "message": "没有接收到图片"
            }), 400

        file = request.files["image"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "message": "没有选择图片"
            }), 400

        # ==============================
        # 2. 打开图片
        # ==============================
        image = Image.open(
            file.stream
        )

        # ==============================
        # 3. 预处理
        # ==============================
        image = preprocess_image(image)



        # ==============================
        # 4. 转换为 NumPy
        # ==============================
        image_array = np.asarray(
            image,
            dtype=np.float64
        )

        # ==============================
        # 5. 784 个输入节点
        # ==============================
        inputs = image_array.reshape(784)

        # ==============================
        # 6. MNIST 输入范围
        # ==============================
        inputs = (
            inputs / 255.0 * 0.99
        ) + 0.01

        # ==============================
        # 7. 神经网络预测
        # ==============================
        outputs = network.query(
            inputs
        )

        # ==============================
        # 8. 得到预测数字
        # ==============================
        prediction = int(
            np.argmax(outputs)
        )

        print(
            "预测结果：",
            prediction
        )

        # ==============================
        # 9. 返回结果
        # ==============================
        return jsonify({
            "success": True,
            "prediction": prediction
        })

    except Exception as e:

        print(
            "识别错误：",
            e
        )

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )