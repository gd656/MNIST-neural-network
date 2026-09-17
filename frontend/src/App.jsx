import { useState } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // 选择图片
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    // 判断是否为图片
    if (!file.type.startsWith("image/")) {
      setMessage("请选择图片文件");
      return;
    }

    setSelectedFile(file);

    // 创建图片预览
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    // 清除之前的识别结果
    setPrediction(null);
    setMessage("");
  };

  // 上传图片并进行识别
  const handlePredict = async () => {
    if (!selectedFile) {
      setMessage("请先选择一张图片");
      return;
    }

    setLoading(true);
    setPrediction(null);
    setMessage("");

    try {
      // 创建 FormData
      const formData = new FormData();

      // image 必须和 Flask 中 request.files["image"] 对应
      formData.append("image", selectedFile);

      // 发送给 Flask 后端
      const response = await fetch(
        "http://127.0.0.1:5000/api/predict",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (data.success) {
        setPrediction(data.prediction);
        setMessage("识别成功");
      } else {
        setMessage(data.message || "识别失败");
      }

    } catch (error) {
      console.error(error);
      setMessage("无法连接后端服务器，请检查 Flask 是否启动");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      <div className="container">

        <h1>MNIST 手写数字识别系统</h1>

        <p className="description">
          上传一张手写数字图片，系统将使用神经网络进行识别
        </p>

        {/* 图片预览 */}
        <div className="preview-container">

          {previewUrl ? (
            <img
              src={previewUrl}
              alt="预览"
              className="preview-image"
            />
          ) : (
            <div className="preview-placeholder">
              请先选择一张图片
            </div>
          )}

        </div>

        {/* 选择图片 */}
        <div className="button-group">

          <label className="select-button">
            选择图片

            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              hidden
            />
          </label>

          {/* 开始识别 */}
          <button
            className="predict-button"
            onClick={handlePredict}
            disabled={!selectedFile || loading}
          >
            {loading ? "识别中..." : "开始识别"}
          </button>

        </div>

        {/* 文件名称 */}
        {selectedFile && (
          <p className="file-name">
            当前图片：{selectedFile.name}
          </p>
        )}

        {/* 状态信息 */}
        {message && (
          <p className="message">
            {message}
          </p>
        )}

        {/* 识别结果 */}
        {prediction !== null && (
          <div className="result">

            <div className="result-title">
              识别结果
            </div>

            <div className="result-number">
              {prediction}
            </div>

          </div>
        )}

      </div>

    </div>
  );
}

export default App;