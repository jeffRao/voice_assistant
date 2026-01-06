# 🎙️ 语音助手项目

一个基于Python的智能语音助手系统，支持语音识别(ASR)、大模型对话(LLM)和语音合成(TTS)的完整流程。

## ✨ 项目功能

本项目构建一个简单的语音助手，通过麦克风收音，语音识别ASR获取用户内容，然后调用大模型获取回答。再通过TTS转化为回答语音，并通过扬声器播放。

### 核心模块

1. **ASR模块**：语音识别模块，使用本地模型进行ASR推理，可以使用FunASR中的小模型进行快速推理，例如SenseVoice
2. **大模型调用模块**：使用OpenAI客户端调用远程大模型，支持配置多种模型
3. **TTS模块**：使用本地推理进行TTS转化，模块化设计支持适配多种TTS。默认支持EdgeTTS和CosyVoice
4. **语音播放模块**：异步播放TTS生成的语音文件
5. **Web界面**：提供友好的Web前端，支持模型选择和录音控制

### 技术特点

- ✅ **流式响应**：大模型流式返回，检测到完整句子立即进行TTS转换，加快响应速度
- ✅ **异步处理**：TTS合成和音频播放完全异步，提升用户体验
- ✅ **模块化设计**：支持轻松扩展更多ASR和TTS模型
- ✅ **会话管理**：每次对话创建独立会话ID，音频文件按会话组织存储
- ✅ **CPU推理**：完全运行在CPU环境下，无需GPU

## 📋 所需模型列表

### ASR模型（二选一）

| 模型名称 | 模型路径 | 说明 | 来源 |
|---------|---------|------|------|
| SenseVoice | `pretrain_models/sensevoice` | 阿里达摩院开源的多语言语音识别模型，支持中英文混合识别 | [ModelScope](https://modelscope.cn/models/iic/SenseVoiceSmall) |
| FunASR | `pretrain_models/funasr` | FunASR框架的中文语音识别模型，轻量快速 | [ModelScope](https://modelscope.cn/models/damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch) |

### TTS模型（二选一）

| 模型名称 | 模型路径 | 说明 | 来源 |
|---------|---------|------|------|
| EdgeTTS | 无需本地模型 | 微软Edge浏览器的在线TTS服务，支持多种中文音色，无需下载模型 | 在线服务 |
| CosyVoice | `pretrain_models/cosyvoice` | 阿里开源的高质量语音合成模型，支持零样本语音克隆 | [ModelScope](https://modelscope.cn/models/iic/CosyVoice-300M) |

### 大模型

| 类型 | 配置项 | 说明 |
|------|--------|------|
| OpenAI兼容API | `config.yaml`中配置 | 支持OpenAI API或任何兼容OpenAI接口的大模型服务（如DeepSeek、Qwen等） |

### 模型下载说明

**EdgeTTS**：无需下载，直接使用在线服务

**其他模型**：需要从ModelScope下载并放置在对应目录

```bash
# 目录结构示例
pretrain_models/
├── sensevoice/          # SenseVoice模型文件
│   ├── model.pt
│   ├── config.yaml
│   └── ...
├── funasr/              # FunASR模型文件
│   ├── model.pt
│   ├── config.yaml
│   └── ...
└── cosyvoice/           # CosyVoice模型文件（可选）
    ├── model.pt
    ├── config.yaml
    └── ...
```

## 🚀 快速开始

### 环境要求

- Python 3.11
- Windows/Linux/MacOS
- 麦克风和扬声器设备

### 安装步骤

1. **克隆项目**

```bash
cd voice_assistant
```

2. **创建虚拟环境（推荐）**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **准备模型文件**

- 从ModelScope下载所需的ASR和TTS模型
- 将模型文件放置在 `pretrain_models/` 目录下
- 如果使用EdgeTTS，可以跳过TTS模型下载

5. **配置文件**

编辑 `config.yaml` 文件，填入您的OpenAI API配置：

```yaml
llm:
  api_key: "your-api-key-here"          # 填入您的API密钥
  base_url: "https://api.openai.com/v1"  # API地址
  model: "gpt-3.5-turbo"                 # 模型名称
  temperature: 0.7
  max_tokens: 2000
```

### 运行项目

```bash
python main.py
```

服务启动后，在浏览器中访问：

```
http://localhost:8000
```

## 📖 使用说明

### Web界面操作

1. **选择模型**
   - 在页面上方选择ASR模型（SenseVoice或FunASR）
   - 选择TTS模型（EdgeTTS或CosyVoice）

2. **开始对话**
   - 点击「开始录音」按钮
   - 对着麦克风说话
   - 点击「停止录音」按钮结束录音

3. **查看结果**
   - 「识别结果」区域显示ASR识别的文本
   - 「AI回答」区域实时显示大模型的回答
   - 系统会自动播放TTS生成的语音

4. **会话管理**
   - 每次点击开始录音前，系统会自动创建新会话
   - 生成的音频文件保存在 `output/会话ID/` 目录下

### 配置说明

#### config.yaml 配置项

```yaml
server:
  host: "0.0.0.0"    # 服务器地址
  port: 8000          # 服务器端口

asr:
  models:
    sensevoice:
      model_path: "pretrain_models/sensevoice"
      language: "auto"  # 自动检测语言
    funasr:
      model_path: "pretrain_models/funasr"
      language: "zh"    # 中文

llm:
  api_key: "your-api-key-here"
  base_url: "https://api.openai.com/v1"
  model: "gpt-3.5-turbo"
  temperature: 0.7    # 生成温度，越高越随机
  max_tokens: 2000    # 最大生成token数
  stream: true        # 启用流式返回

tts:
  models:
    edgetts:
      voice: "zh-CN-XiaoxiaoNeural"  # 中文女声
      rate: "+0%"      # 语速
      volume: "+0%"    # 音量
    cosyvoice:
      model_path: "pretrain_models/cosyvoice"
      speaker: "default"

audio:
  sample_rate: 16000  # 采样率
  channels: 1         # 声道数
  chunk_size: 1024    # 音频块大小
  format: "wav"       # 音频格式

output:
  dir: "output"       # 输出目录
  audio_format: "wav" # 输出音频格式

sentence_delimiters: ["。", "！", "？", ".", "!", "?"]  # 句子分隔符
```

## 📁 项目结构

```
voice_assistant/
├── asr/                    # ASR语音识别模块
│   ├── __init__.py
│   ├── base_asr.py        # ASR基类
│   ├── sensevoice_asr.py  # SenseVoice实现
│   ├── funasr_asr.py      # FunASR实现
│   └── asr_factory.py     # ASR工厂类
├── llm/                    # 大模型调用模块
│   ├── __init__.py
│   └── llm_client.py      # OpenAI客户端
├── tts/                    # TTS语音合成模块
│   ├── __init__.py
│   ├── base_tts.py        # TTS基类
│   ├── edge_tts.py        # EdgeTTS实现
│   ├── cosyvoice_tts.py   # CosyVoice实现
│   └── tts_factory.py     # TTS工厂类
├── audio/                  # 音频处理模块
│   ├── __init__.py
│   ├── player.py          # 音频播放器
│   └── recorder.py        # 音频录制器
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── config_loader.py   # 配置加载器
│   └── session.py         # 会话管理器
├── static/                 # 前端静态文件
│   └── index.html         # Web界面
├── pretrain_models/        # 预训练模型目录
├── output/                 # 输出文件目录
├── app.py                  # FastAPI后端服务
├── main.py                 # 主程序入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖文件
├── .gitignore             # Git忽略文件
└── README.md              # 项目说明
```

## 🔧 常见问题

### 1. 模型加载失败

- 检查模型文件是否完整下载
- 确认模型路径配置正确
- 查看控制台错误信息

### 2. 麦克风无法使用

- 检查浏览器是否授予麦克风权限
- 确认系统麦克风设备正常工作
- 尝试在HTTPS环境下使用（或localhost）

### 3. 音频无法播放

- 检查系统扬声器设备
- 确认音频文件生成成功
- 查看浏览器控制台错误

### 4. API调用失败

- 检查API密钥是否正确
- 确认网络连接正常
- 验证API额度是否充足

### 5. PyAudio安装失败（Windows）

```bash
# 可以从这里下载预编译的whl文件
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio-0.2.14-cp311-cp311-win_amd64.whl
```

## 🛠️ 技术栈

- **后端框架**：FastAPI + Uvicorn
- **ASR引擎**：FunASR (SenseVoice/FunASR)
- **LLM客户端**：OpenAI Python SDK
- **TTS引擎**：EdgeTTS / CosyVoice
- **音频处理**：PyAudio + Pygame
- **前端**：原生HTML + JavaScript + WebSocket

## 📝 开发说明

### 扩展新的ASR模型

1. 在 `asr/` 目录下创建新的模型类，继承 `BaseASR`
2. 实现 `load_model()` 和 `transcribe()` 方法
3. 在 `asr_factory.py` 中注册新模型

### 扩展新的TTS模型

1. 在 `tts/` 目录下创建新的模型类，继承 `BaseTTS`
2. 实现 `synthesize()` 和 `synthesize_sync()` 方法
3. 在 `tts_factory.py` 中注册新模型

## 📄 License

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**：使用本项目前，请确保已准备好所需的模型文件和API密钥。