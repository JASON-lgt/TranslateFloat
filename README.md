# 翻译飘窗

Windows 置顶翻译小工具：透明区识别屏幕文字、剪贴板翻译、按住说话。  
**免费开源 · 自愿支持**（支持不解锁任何功能）。

## 快速开始（开发）

1. 安装依赖（已有 `.venv` 可跳过）：

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

2. 双击 `启动翻译.bat`

## 发布安装包

```powershell
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

得到 zip 后上传到 GitHub / Gitee Release。详见 [`RELEASE.md`](./RELEASE.md)。

详细说明见 `使用说明.txt`。开源清单见 `开源发布清单.md`。
## 功能

- 透明识别区 OCR → 翻译（默认约 4 秒间隔）
- 剪贴板自动译
- 按住说话（Whisper tiny）
- 设置中可切换翻译引擎；可选填写 DeepL API Key

## 支持作者

自愿支持（支付宝），见 [SUPPORT.md](./SUPPORT.md)。  
收款码：[`assets/donate.png`](./assets/donate.png)。软件内点 **支持** 也可查看。

请以本仓库为准；修改版请自行甄别。

## 免责声明

- 默认翻译走第三方网页接口或你自备的 API，可用性与条款由各服务方决定。  
- 仅供学习与个人使用；请遵守当地法律与服务条款。  
- 软件按 MIT 许可「原样」提供，作者不承担使用后果。

## 许可证

[MIT](./LICENSE)

## 作者

空白
