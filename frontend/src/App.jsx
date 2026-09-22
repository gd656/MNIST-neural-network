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
      // 使用相