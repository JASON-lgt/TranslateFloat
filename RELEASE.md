# 发布到 GitHub / Gitee Release

## 1. 本地打包

在项目目录打开 PowerShell：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_release.ps1
```

成功后产物一般在：

- `E:\translate-float-build\TranslateFloat-v1.0.0-windows-x64.zip`
- `E:\translate-float-build\TranslateFloat-v1.0.0-windows-x64.zip.sha256`

（若没有 E: 盘，则在项目下 `release_build\`）

用户用法：解压 zip → 双击 `TranslateFloat.exe`

## 2. GitHub Release

1. 推送代码到 GitHub 仓库  
2. Releases → **Draft a new release**  
3. Tag：`v1.0.0`（与 `services/branding.py` 里 `APP_VERSION` 一致）  
4. 标题例如：`翻译飘窗 v1.0.0`  
5. 上传 zip 与 sha256 文件  
6. 描述可粘贴下方模板  

## 3. Gitee Release

1. 推送代码到 Gitee  
2. 发行版 → 创建发行版  
3. 同样上传 zip / sha256，填写说明  

## 4. Release 说明模板

```markdown
## 翻译飘窗 v1.0.0

免费开源的 Windows 置顶翻译工具（透明区 OCR / 剪贴板 / 语音）。

### 使用

1. 下载 `TranslateFloat-v1.0.0-windows-x64.zip`
2. 解压到任意目录（建议纯英文路径）
3. 运行 `TranslateFloat.exe`
4. 首次屏幕识别 / 语音可能需联网下载模型

### 校验

请核对附带的 `.sha256` 文件。

### 说明

- 自愿支持作者：软件内「支持」或见仓库 `SUPPORT.md`
- 默认翻译走第三方接口；可在设置中填写自备 DeepL Key
- 需要截屏、剪贴板、麦克风、网络权限

### 已知限制

- 体积较大（含 OCR / 语音相关组件）
- 未做代码签名时，SmartScreen 可能提示「未知应用」，选仍要运行即可
```

## 5. 改版本号

发布新版本前，只改：

`services/branding.py` → `APP_VERSION = "1.0.1"`

然后重新执行 `build_release.ps1`。
