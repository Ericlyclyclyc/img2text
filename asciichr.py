from PIL import Image
import numpy as np

DEFAULT_CHARS = " .:-=+*#%@"

def get_char_for_brightness(brightness, char_set):
    idx = int(brightness / 255 * (len(char_set) - 1))
    return char_set[idx]

def image_to_asciichr(
    image_path: str,
    output_width: int = 80,
    char_set: str = DEFAULT_CHARS,
    bg_color: tuple = (0, 0, 0),
    alpha_threshold: int = 128,
    invert: bool = False
) -> str:
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
                line_parts.append("\033[0m ")
                continue
            r_val, g_val, b_val = rgb_array[y, x]
            brightness = 0.299 * r_val + 0.587 * g_val + 0.114 * b_val
            if invert:
                brightness = 255 - brightness
            ascii_char = get_char_for_brightness(brightness, char_set)
            colored_char = f"\033[38;2;{r_val};{g_val};{b_val}m{ascii_char}"
            line_parts.append(colored_char)
        lines.append("".join(line_parts) + "\033[0m")

    return lines