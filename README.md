# Img2Text 图片转彩色字符画
<div align=left>
    <img src="https://img.shields.io/badge/python-3.7%2B-blue"/>
    <img src="https://img.shields.io/github/license/MurthiNext/img2text"/>
    <img src="https://img.shields.io/github/stars/MurthiNext/img2text"/>
</div>

将图片转换为终端字符画的命令行工具，支持 **ASCII 字符**、**盲文点阵 (Braille)** 和 **半色块 (▀)** 三种风格，均保留原始图像颜色，并支持透明 PNG。

## ✨ 特性

- 🎨 **全彩色输出** – 使用 ANSI 转义序列为每个字符/色块设置前景色或背景色
- 🖼️ **透明支持** – 自动识别透明区域，输出为空格并重置样式
- 🔠 **三种渲染模式** – 一次运行同时生成三种风格的字符画
- ⚙️ **可调参数** – 输出宽度、对比度、锐化、自适应阈值（盲文模式）、透明度阈值等

## 📦 依赖

- Python 3.7+
- [Pillow](https://python-pillow.org) (PIL)
- [NumPy](https://numpy.org)
- [SciPy](https://scipy.org)（仅 `braille.py` 需要）

安装依赖：

```bash
pip install pillow numpy scipy
```

## 🚀 命令行使用

将 `braille.py`、`colorblocks.py`、`asciichr.py`、`img2text.py` 放在同一目录，执行：

```bash
python img2text.py <图片路径> <输出宽度>
```

或打包为 `img2text.exe` 后直接运行：

```bash
img2text.exe <图片路径> <输出宽度>
```

**示例**：

```bash
python img2text.py 1.png 80
```

### 输出说明

- **终端显示**：三种风格的结果并排显示，每行依次为：ASCII 结果行 + 三个空格 + 盲文结果行 + 三个空格 + 半色块结果行
- **文件保存**：
  - `a.txt` – ASCII 字符画
  - `b.txt` – 盲文字符画
  - `c.txt` – 半色块字符画

所有文件均以 UTF-8 编码保存，可直接在支持 ANSI 颜色的终端中查看或使用 `cat`/`type` 命令显示。

## 📖 模块调用（可选）

你也可以在 Python 脚本中单独调用各个模块：

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

### 函数签名

#### `asciichr.py`

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

#### `braille.py`

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

#### `colorblocks.py`

```python
image_to_color_blocks(
    image_path: str,
    output_width: int = 80,
    scale: float = 1.0,
    alpha_threshold: int = 128
) -> List[str]
```

每个终端字符显示 **上下两个像素**（上像素作为前景色，下像素作为背景色，字符固定为 `▀`）。  
透明区域（上下任一像素透明）输出为空格。

| 参数 | 说明 |
|------|------|
| `scale` | 高度缩放系数（宽高比校正） |
| `alpha_threshold` | Alpha > 此值视为不透明 |

## 🖥️ 终端兼容性

- 需要支持 **真彩色**（24-bit ANSI 颜色）的终端：
  - Windows Terminal (>=1.0)
  - macOS Terminal (iTerm2, Terminal.app 支持较好)
  - Linux (GNOME Terminal, Konsole, etc.)
- 盲文字符需要终端字体支持 Unicode 范围 `U+2800–U+28FF`（现代终端基本都支持）。

## 📄 示例

运行 `python img2text.py logo.png 100` 后，终端输出类似：

```
ASCII结果行   盲文结果行   半色块结果行
...           ...         ...
```

同时生成 `a.txt`、`b.txt`、`c.txt` 三个文件。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request。

## 📜 许可证

本项目采用 **MIT 许可证**。详情请参阅 [LICENSE](LICENSE) 文件。