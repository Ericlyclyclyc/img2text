from PIL import Image
import numpy as np

def color_distance(c1, c2):
    """计算两个RGB颜色的欧氏距离"""
    return sum((int(a) - int(b)) ** 2 for a, b in zip(c1, c2)) ** 0.5

def image_to_color_blocks(
    image_path: str,
    output_width: int = 80,
    scale: float = 1.0,
    bg_color: tuple = (0, 0, 0),
    black_tolerance: float = 30.0
) -> str:
    """
    将图片转换为彩色块字符画。
    """
    # 打开图片，处理透明度
    img = Image.open(image_path).convert("RGBA")
    bg_img = Image.new("RGBA", img.size, (*bg_color, 255))
    img = Image.alpha_composite(bg_img, img).convert("RGB")

    # 计算目标像素尺寸
    pixel_width = output_width
    pixel_height = int(pixel_width * img.height / img.width * scale)
    pixel_height = pixel_height if pixel_height % 2 == 0 else pixel_height + 1

    img = img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
    pixels = np.array(img)

    lines = []
    black_rgb = (0, 0, 0)

    for y in range(0, pixel_height, 2):
        line_parts = []
        for x in range(pixel_width):
            top = tuple(pixels[y, x])
            bottom = tuple(pixels[y+1, x]) if y+1 < pixel_height else bg_color

            top_is_black = color_distance(top, black_rgb) < black_tolerance
            bottom_is_black = color_distance(bottom, black_rgb) < black_tolerance

            # 情况1：上下都是黑色 -> 输出重置样式后的空格（完全透明，无颜色残留）
            if top_is_black and bottom_is_black:
                line_parts.append("\033[0m ")   # 先重置，再空格
                continue

            # 构建 ANSI 代码
            codes = []
            if not top_is_black:
                codes.append(f"\033[38;2;{top[0]};{top[1]};{top[2]}m")
            if not bottom_is_black:
                codes.append(f"\033[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m")
            codes.append("▀")
            line_parts.append("".join(codes))

        # 行末重置样式并换行
        lines.append("".join(line_parts) + "\033[0m")
    return lines