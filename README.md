# Img2Text 图片转彩色字符画
<div align=left>
    <img src="https://img.shields.io/badge/python-3.7%2B-blue"/>
    <img src="https://img.shields.io/github/license/MurthiNext/img2text"/>
    <img src="https://img.shields.io/github/stars/MurthiNext/img2text"/>
</div>

将图片转换为终端字符画的 Python 工具集，支持 **ASCII 字符**、**盲文点阵 (Braille)** 和 **半色块 (▀)** 三种风格，均保留原始图像颜色，并支持透明 PNG。

## ✨ 特性

- 🎨 **全彩色输出** – 使用 ANSI 转义序列为每个字符/色块设置前景色或背景色
- 🖼️ **透明支持** – 自动识别透明区域，输出为空格并重置样式
- 🔠 **三种渲染模式**
  - **ASCII 字符** – 根据亮度映射到自定义字符集（默认 ` .:-=+*#%@`）
  - **盲文点阵** – 利用 Unicode 盲文字符（U+2800~U+28FF）实现 2×4 分辨率压缩
  - **彩色半块** – 使用 `▀` 字符，上/下像素分别对应前景/背景色，实现垂直双倍精度
- ⚙️ **可调参数** – 输出宽度、对比度、锐化、自适应阈值（盲文模式）、背景色等

## 📦 依赖

- Python 3.7+
- [Pillow](https://python-pillow.org) (PIL)
- [NumPy](https://numpy.org)
- [SciPy](https://scipy.org)（仅 `braille.py` 需要）

安装依赖：

```bash
pip install pillow numpy scipy
```

## 🚀 快速开始

### 1. 克隆或下载代码
将 `braille.py`、`colorblocks.py`、`asciichr.py`、`img2text.py` 放在同一目录。

### 2. 准备图片
例如图片名为 `1.png`。

### 3. 运行示例
直接执行 `img2text.py`（会生成三份结果并打印对比）：

```bash
python img2text.py
```

或在代码中单独调用：

```python
from asciichr import image_to_asciichr
from braille import image_to_braille
from colorblocks import image_to_color_blocks

# ASCII 模式
ascii_lines = image_to_asciichr('1.png', output_width=80)

# 盲文模式
braille_lines = image_to_braille('1.png', output_width=80)

# 半块模式
block_lines = image_to_color_blocks('1.png', output_width=80)
```

### 4. 保存到文件
每个函数返回字符串列表，可写入 `.txt` 文件（注意终端需支持 ANSI 颜色）。

## 📖 模块说明

### `asciichr.py` – ASCII 字符画

```python
image_to_asciichr(
    image_path: str,
    output_width: int = 80,
    char_set: str = " .:-=+*#%@",
    bg_color: tuple = (0, 0, 0),
    alpha_threshold: int = 128,
    invert: bool = False
) -> List[str]
```

| 参数 | 说明 |
|------|------|
| `output_width` | 输出字符宽度（像素/列数） |
| `char_set` | 亮度映射的字符集（由暗到亮） |
| `bg_color` | 透明区域填充的背景色 (R,G,B) |
| `alpha_threshold` | Alpha > 此值视为不透明 |
| `invert` | 是否反转亮度映射 |

### `braille.py` – 盲文字符画

```python
image_to_braille(
    image_path: str,
    output_width: int = 80,
    sharpen_strength: float = 1.2,
    contrast_factor: float = 1.5,
    sigma: float = 3.0,
    k: float = 0.4,
    alpha_threshold: int = 128
) -> List[str]
```

每个盲文字符对应原始图像的 **2 像素宽 × 4 像素高** 区域。  
使用自适应阈值（局部均值 − k×局部标准差）生成点阵。

| 参数 | 说明 |
|------|------|
| `sharpen_strength` | 锐化强度，>1 增强边缘 |
| `contrast_factor` | 对比度因子 |
| `sigma` | 高斯滤波标准差（决定局部区域大小） |
| `k` | 阈值偏移系数，越大越容易点亮 |
| `alpha_threshold` | 透明判定阈值 |

### `colorblocks.py` – 半色块字符画

```python
image_to_color_blocks(
    image_path: str,
    output_width: int = 80,
    scale: float = 1.0,
    bg_color: tuple = (0, 0, 0),
    black_tolerance: float = 30.0
) -> List[str]
```

每个终端字符显示 **上下两个像素**（上像素作为前景色，下像素作为背景色，字符固定为 `▀`）。  
若上下均为黑色（或接近背景色），则输出普通空格。

| 参数 | 说明 |
|------|------|
| `scale` | 高度缩放系数（宽高比校正） |
| `bg_color` | 背景色，也用于判定“黑色”的参考 |
| `black_tolerance` | 颜色欧氏距离小于此值视为黑色 |

## 🖥️ 终端兼容性

- 需要支持 **真彩色**（24-bit ANSI 颜色）的终端：
  - Windows Terminal (>=1.0)
  - macOS Terminal (iTerm2, Terminal.app 支持较好)
  - Linux (GNOME Terminal, Konsole, etc.)
- 盲文字符需要终端字体支持 Unicode 范围 `U+2800–U+28FF`（现代终端基本都支持）。

## 📄 示例输出

运行 `python img2text.py` 后会在控制台并列显示三种效果（由于 Markdown 无法渲染 ANSI 颜色，仅示意布局）：

```
ASCII结果行   Braille结果行   ColorBlock结果行
...           ...            ...
```

同时生成三个文本文件：
- `ascii_result.txt`
- `braille_result.txt`
- `color_blocks_result.txt`

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。

## 📜 许可证

本项目采用 **MIT 许可证**。详情请参阅 [LICENSE](LICENSE) 文件。