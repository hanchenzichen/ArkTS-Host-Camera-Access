# ArkTS-Host-Camera-Access

A sample DevEco Studio project demonstrating how to access the host machine's camera for photo capture and video recording in a HarmonyOS emulator.

一个演示如何在鸿蒙模拟器中调用宿主机摄像头进行拍照和录像的DevEco Studio示例项目。

[![Language: ArkTS](https://img.shields.io/badge/Language-ArkTS-blue.svg)](https://developer.harmonyos.com/) [![Language: Python](https://img.shields.io/badge/Language-Python-yellow.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🏗️ 项目架构 (Project Architecture)

本项目采用客户端-服务器 (C/S) 架构，由两部分组成：

1.  **前端 (Frontend)**: 一个用 ArkTS 编写的 HarmonyOS 应用。它运行在 DevEco Studio 的模拟器中，提供用户操作界面。
2.  **后端 (Backend)**: 一个用 Python、Flask 和 OpenCV 构建的轻量级本地服务器。它运行在你的电脑（宿主机）上，负责直接控制摄像头并将视频流和功能通过 API 暴露出来。

**工作流程:**
`HarmonyOS App (模拟器中) <--> 局域网HTTP请求 <--> Python后端服务 (电脑上)`

## ✨ 主要功能 (Features)

- **实时摄像头预览**: 在鸿蒙应用中实时显示电脑摄像头的画面。
- **拍照与录制**: 捕获画面或录制视频，并保存在后端服务器上。
- **摄像头切换**: 支持在多个摄像头设备之间切换。
- **断线重连**: 当应用与后端服务断开连接时，会自动尝试重连。
- **三级页面导航**:
    1.  **拍摄页**: 主交互界面，用于预览和控制。
    2.  **相册管理页**: 远程浏览、下载或删除服务器上的文件。
    3.  **文件预览页**: 全屏查看指定的图片或播放视频。
- **强大的文件管理**:
    - 下载文件到设备公共相册，包含完整的运行时权限请求逻辑 (`ohos.permission.WRITE_MEDIA`)。
    - 从服务器上远程删除指定文件。

## 🔧 环境准备 (Prerequisites)

- **DevEco Studio**: 最新版本。
- **Node.js 和 npm**: DevEco Studio 所需。
- **Python**: 3.7 或更高版本。
- **pip**: Python 包管理器。

## 🚀 快速开始 (Getting Started)

### **第一步：设置后端服务 (Python)**

1.  **克隆或下载仓库**
    ```bash
    git clone https://github.com/your-username/ArkTS-Host-Camera-Access.git
    cd ArkTS-Host-Camera-Access
    ```
2.  **进入后端代码目录并安装依赖**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
3.  **运行后端服务**
    ```bash
    python app.py
    ```
    服务启动后将监听在 `5000` 端口。

### **第二步：设置前端应用 (HarmonyOS)**

1.  **打开项目**
    使用 DevEco Studio 打开仓库中的 `frontend` 文件夹。

2.  **声明权限 (重要！)**
    应用需要网络和存储权限才能正常工作。打开 `entry/src/main/module.json5` 文件，确保 `requestPermissions` 字段包含了以下内容：

    ```json5
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET"
      },
      {
        "name": "ohos.permission.WRITE_MEDIA",
        "reason": "$string:write_media_reason",
        "usedScene": {
          "abilities": [ "EntryAbility" ],
          "when": "inuse"
        }
      }
    ]
    ```
    > **提示**: 同时需要在 `entry/src/main/resources/base/element/string.json` 中为 `write_media_reason` 添加说明。

3.  **修改后端服务地址**
    在所有 `ets` 页面文件 (`CameraPhoto.ets`, `PhotoAlbum.ets`, `FilePreviewPage.ets`) 中，找到下面这行代码：

    ```typescript
    private serverHost: string = "http://10.0.2.2:5000";
    ```
    -   **使用 DevEco Studio 模拟器时**: **无需修改**。`10.0.2.2` 是模拟器访问宿主机（你的电脑）的特殊地址。
    -   **使用实体手机或第三方模拟器时**: 将 `10.0.2.2` 替换为你电脑的局域网 IP 地址（例如 `192.168.1.10`）。
    -   **监听地址**:可将其设置为0.0.0.0，所有地址都可以访问，这样无论是局域网还是localhost或者是127.0.0.1都可以访问。

4.  **运行应用**
    选择配置好的模拟器作为目标设备，点击 "Run" 运行项目。

## 📁 项目结构 (Project Structure)

```
ArkTS-Host-Camera-Access/
├── backend/                  # 后端服务代码
│   ├── app.py                # Flask 主程序
│   └── requirements.txt      # Python 依赖
│
├── frontend/                 # 前端鸿蒙工程
│   ├── entry/src/main/
│   │   ├── ets/pages/
│   │   │   ├── CameraPhoto.ets     # 实时拍摄页面 (应用主页)
│   │   │   ├── PhotoAlbum.ets      # 相册管理页 (列出、下载、删除文件)
│   │   │   └── FilePreviewPage.ets # 文件预览页 (全屏查看图片/视频)
│   │   ├── module.json5         # 权限声明在这里
│   │   └── ...
│   └── ... (其他DevEco Studio项目文件)
│
└── README.md                 # 就是这个文件
```

<details>
<summary><b>📖 点击展开/折叠 API 接口文档</b></summary>

---

#### 摄像头控制

-   `GET /frame`: 获取一帧摄像头画面（用于视频流）。
-   `GET /snapshot`: 拍摄一张照片并保存。
-   `POST /record/start`: 开始录制视频。
-   `POST /record/stop`: 停止录制视频。
-   `POST /switch`: 切换摄像头，请求体为 `{"index": 1}`。

#### 文件管理

-   `GET /files`: 获取服务器上所有媒体文件的列表。
-   `GET /view/<filename>`: 在线预览指定的文件。
-   `GET /download/<filename>`: 下载指定文件。
-   `DELETE /delete/<filename>`: 删除指定文件。

---
</details>

## 🤝 贡献 (Contributing)

欢迎提交问题 (Issues) 和合并请求 (Pull Requests)。

## 📄 许可证 (License)

本项目采用 MIT 许可证。````
