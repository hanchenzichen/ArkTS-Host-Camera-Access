# ArkTS-Host-Camera-Access

A sample DevEco Studio project demonstrating how to access the host machine's camera for photo capture and video recording in a HarmonyOS emulator.

一个演示如何在鸿蒙模拟器中调用宿主机摄像头进行拍照和录像的DevEco Studio示例项目。

[![Language: ArkTS](https://img.shields.io/badge/Language-ArkTS-blue.svg)](https://developer.harmonyos.com/) [![Language: Python](https://img.shields.io/badge/Language-Python-yellow.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🏗️ 项目架构 (Project Architecture)

This project uses a Client-Server (C/S) architecture, consisting of two main parts:
本项目采用客户端-服务器 (C/S) 架构，由两部分组成：

1.  **Frontend (前端)**: A HarmonyOS application written in ArkTS. It runs in the DevEco Studio emulator and provides the user interface.
    一个用 ArkTS 编写的 HarmonyOS 应用。它运行在 DevEco Studio 的模拟器中，提供用户操作界面。

2.  **Backend (后端)**: A lightweight local server built with Python, Flask, and OpenCV. It runs on your host machine (computer), responsible for directly controlling the camera and exposing its functionalities via API.
    一个用 Python、Flask 和 OpenCV 构建的轻量级本地服务器。它运行在你的电脑（宿主机）上，负责直接控制摄像头并将视频流和功能通过 API 暴露出来。

**Workflow (工作流程):**
`HarmonyOS App (in emulator) <--> LAN HTTP Requests <--> Python Backend Service (on computer)`
`HarmonyOS App (模拟器中) <--> 局域网HTTP请求 <--> Python后端服务 (电脑上)`

## ✨ 主要功能 (Features)

-   **Real-time Camera Preview (实时摄像头预览)**: Display the host machine's camera feed in real-time within the HarmonyOS application.
    在鸿蒙应用中实时显示电脑摄像头的画面。
-   **Photo Capture & Video Recording (拍照与录制)**: Capture the current frame or record a video stream and save it on the backend server.
    捕获画面或录制视频，并保存在后端服务器上。
-   **Camera Switching (摄像头切换)**: Supports switching between multiple camera devices.
    支持在多个摄像头设备之间切换。
-   **Disconnection & Reconnection (断线重连)**: Automatically attempts to reconnect when the application loses connection to the backend service.
    当应用与后端服务断开连接时，会自动尝试重连。
-   **Three-Level Page Navigation (三级页面导航)**:
    1.  **Shooting Page (拍摄页)**: The main interactive interface for preview and control.
        主交互界面，用于预览和控制。
    2.  **Album Management Page (相册管理页)**: Remotely browse, download, or delete files on the server.
        远程浏览、下载或删除服务器上的文件。
    3.  **File Preview Page (文件预览页)**: View specified images or play videos in full screen.
        全屏查看指定的图片或播放视频。
-   **Powerful File Management (强大的文件管理)**:
    -   Download files to the device's public photo album, including complete runtime permission request logic (`ohos.permission.WRITE_MEDIA`).
        下载文件到设备公共相册，包含完整的运行时权限请求逻辑 (`ohos.permission.WRITE_MEDIA`)。
    -   Remotely delete specified files from the server.
        从服务器上远程删除指定文件。

## 🔧 环境准备 (Prerequisites)

-   **DevEco Studio**: Latest version.
-   **Node.js and npm**: Required by DevEco Studio.
-   **Python**: 3.7 or higher.
-   **pip**: Python package manager.

## 🚀 快速开始 (Getting Started)

### **Step 1: Set Up the Backend Service (第一步：设置后端服务 Python)**

1.  **Clone or download the repository (克隆或下载仓库)**
    ```bash
    git clone https://github.com/your-username/ArkTS-Host-Camera-Access.git
    cd ArkTS-Host-Camera-Access
    ```
2.  **Navigate to the backend directory and install dependencies (进入后端代码目录并安装依赖)**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
3.  **Run the backend service (运行后端服务)**
    ```bash
    python camera_server.py
    ```
    The service will start and listen on port `5000`.
    服务启动后将监听在 `5000` 端口。

### **Step 2: Set Up the Frontend Application (第二步：设置前端应用 HarmonyOS)**

1.  **Open the project (打开项目)**
    Unzip the `frontend` compressed package downloaded locally to the current directory.
    将下载到本地的`frontend`压缩包解压到当前目录下
    Open the `frontend` folder from the repository using DevEco Studio.
    使用 DevEco Studio 打开仓库中的 `frontend` 文件夹。

3.  **Declare permissions (Important!) (声明权限 重要！)**
    The application requires network and storage permissions to function correctly. Open `entry/src/main/module.json5` and ensure the `requestPermissions` field includes the following:
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
    > **Tip (提示)**: You also need to add a description for `write_media_reason` in `entry/src/main/resources/base/element/string.json`.
    > 同时需要在 `entry/src/main/resources/base/element/string.json` 中为 `write_media_reason` 添加说明。

4.  **Modify the backend service address (修改后端服务地址)**
    In all `.ets` page files (`CameraPhoto.ets`, `PhotoAlbum.ets`, `FilePreviewPage.ets`), find the following line:
    在所有 `ets` 页面文件 (`CameraPhoto.ets`, `PhotoAlbum.ets`, `FilePreviewPage.ets`) 中，找到下面这行代码：

    ```typescript
    private serverHost: string = "http://10.0.2.2:5000";
    ```
    -   **When using DevEco Studio Emulator (使用 DevEco Studio 模拟器时)**: **No modification needed (无需修改)**. `10.0.2.2` is a special address for the emulator to access the host machine.
        `10.0.2.2` 是模拟器访问宿主机（你的电脑）的特殊地址。
    -   **When using a physical device or a third-party emulator (使用实体手机或第三方模拟器时)**: Replace `10.0.2.2` with your computer's LAN IP address (e.g., `192.168.1.10`).
        将 `10.0.2.2` 替换为你电脑的局域网 IP 地址（例如 `192.168.1.10`）。
    -   **Listening Address (监听地址)**: The backend is set to `0.0.0.0`, allowing access from all addresses, including LAN, localhost, and 127.0.0.1.
        后端服务已设置为`0.0.0.0`，所有地址都可以访问，这样无论是局域网还是localhost或者是127.0.0.1都可以访问。

5.  **Run the application (运行应用)**
    Select the configured emulator as the target device and click "Run".
    选择配置好的模拟器作为目标设备，点击 "Run" 运行项目。

## 📁 项目结构 (Project Structure)

```
ArkTS-Host-Camera-Access/
├── backend/                  # Backend service code (后端服务代码)
│   ├── camera_server.py      # Main Flask application (Flask 主程序)
│   └── requirements.txt      # Python dependencies (Python 依赖)
│
├── frontend/                 # Frontend HarmonyOS project (前端鸿蒙工程)
│   ├── entry/src/main/
│   │   ├── ets/pages/
│   │   │   ├── CameraPhoto.ets     # Real-time shooting page (app main page) (实时拍摄页面 应用主页)
│   │   │   ├── PhotoAlbum.ets      # Album management page (list, download, delete) (相册管理页 列出、下载、删除文件)
│   │   │   └── FilePreviewPage.ets # File preview page (fullscreen image/video) (文件预览页 全屏查看图片/视频)
│   │   ├── module.json5         # Permission declarations are here (权限声明在这里)
│   │   └── ...
│   └── ... (Other DevEco Studio project files) (其他DevEco Studio项目文件)
│
└── README.md                 # This file (就是这个文件)
```

<details>
<summary><b>📖 Click to expand/collapse API Documentation (点击展开/折叠 API 接口文档)</b></summary>

---

#### Camera Control (摄像头控制)

-   `GET /frame`: Get a camera frame (for video stream).
    获取一帧摄像头画面（用于视频流）。
-   `GET /snapshot`: Take a picture and save it.
    拍摄一张照片并保存。
-   `POST /record/start`: Start recording video.
    开始录制视频。
-   `POST /record/stop`: Stop recording video.
    停止录制视频。
-   `POST /switch`: Switch camera. Request body: `{"index": 1}`.
    切换摄像头，请求体为 `{"index": 1}`。

#### File Management (文件管理)

-   `GET /files`: Get a list of all media files on the server.
    获取服务器上所有媒体文件的列表。
-   `GET /view/<filename>`: Preview a specific file online.
    在线预览指定的文件。
-   `GET /download/<filename>`: Download a specific file.
    下载指定文件。
-   `DELETE /delete/<filename>`: Delete a specific file.
    删除指定文件。

---
</details>

## 🤝 贡献 (Contributing)

Issues and Pull Requests are welcome.
欢迎提交问题 (Issues) 和合并请求 (Pull Requests)。

## ⚠️ 免责声明 (Disclaimer)
This README was generated with the assistance of an AI. In case of any discrepancies between this document and the actual code, please investigate on your own and consider the source code as the single source of truth.

该 `README.md` 文件由 AI 辅助生成。如果文档内容与实际代码存在不一致之处，请自行研究，并以源代码为最终标准。

## 📄 许可证 (License)

This project is licensed under the MIT License.
本项目采用 MIT 许可证。
