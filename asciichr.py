from PIL import Image
import numpy as np

DEFAULT_CHARS = " .:-=+*#%@"

def get_char_for_brightness(brightness, char_set):
    idx = int(brightness / 255 * (len(char_set) - 1))
    return char_set[idx]

def image_to_asciichr(
    image_path: str,
    output_width: int = 50,
    char_set: str = DEFAULT_CHARS,
    bg_color: tuple = (0, 0, 0),
    alpha_threshold: int = 128,
    invert: bool = False,
    colored: bool = True
) -> str:
    """
    将图片转换为彩色 ASCII 字符画（透明区域显示为空格）。

    参数:
        image_path: 图片路径（支持透明 PNG）
        output_width: 输出字符宽度（ASCII字符个数）
        char_set: 用于表示亮度的字符集
        bg_color: 背景色（用于填充透明区域）
        alpha_threshold: Alpha 通道阈值，低于此值视为透明（0~255）
        invert: 是否反转亮度（True表示亮色用深色字符表示，反之亦然）
        colored: 是否输出 ANSI 颜色代码，False 时输出纯字符（保留透明过滤）
    """
    # 1. 打开图片
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()
    alpha_mask = np.array(a) > alpha_threshold

    # 2. 处理透明度：将透明区域填充为背景色，非透明区域保留原色
    bg_img = Image.new("RGBA", img.size, (*bg_color, 255))
    img_filled = Image.alpha_composite(bg_img, img)   # 修正顺序
    img_rgb = img_filled.convert("RGB")

    # 3. 缩放
    aspect_ratio = 0.5
    pixel_width = output_width
    pixel_height = int(pixel_width * img.height / img.width * aspect_ratio)
    pixel_height = max(1, pixel_height)

    rgb_resized = img_rgb.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
    alpha_mask_pil = Image.fromarray(alpha_mask.astype(np.uint8) * 255)
    alpha_resized = alpha_mask_pil.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
    alpha_resized = np.array(alpha_resized) > 128

    rgb_array = np.array(rgb_resized)

    # 4. 生成字符画
    lines = []
    for y in range(pixel_height):
        line_parts = []
        for x in range(pixel_width):
            if not alpha_resized[y, x]:
                # 透明区域：根据 colored 决定是否添加重置序列
                line_parts.append("\033[0m " if colored else " ")
                continue
            r_val, g_val, b_val = rgb_array[y, x]
            brightness = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            if invert:
                brightness = 255 - brightness
            ascii_char = get_char_for_brightness(brightness, char_set)
            if colored:
                colored_char = f"\033[38;2;{r_val};{g_val};{b_val}m{ascii_char}"
            else:
                colored_char = ascii_char
            line_parts.append(colored_char)
        line = "".join(line_parts)
        if colored:
            line += "\033[0m"
        lines.append(line)

    return lines