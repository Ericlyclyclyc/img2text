from PIL import Image
import numpy as np

def image_to_color_blocks(
    image_path: str,
    output_width: int = 80,
    scale: float = 1.0,
    alpha_threshold: int = 128
) -> str:
    """
    将图片转换为彩色块字符画（透明区域显示为空格）。

    参数:
        image_path: 图片路径（支持透明 PNG）
        output_width: 输出字符宽度（每个字符代表 2x1 像素块）
        scale: 高度缩放因子（相对于宽度）
        alpha_threshold: Alpha 通道阈值，低于此值视为透明（0~255）
    """
    # 1. 打开图片，保留 Alpha 通道
    img = Image.open(image_path).convert("RGBA")
    r, g, b, a = img.split()
    alpha_mask = np.array(a) > alpha_threshold

    # 2. 计算目标像素尺寸（宽 = output_width，高按比例缩放并保证偶数）
    pixel_width = output_width
    pixel_height = int(pixel_width * img.height / img.width * scale)
    pixel_height = pixel_height if pixel_height % 2 == 0 else pixel_height + 1

    # 3. 缩放 RGB 通道（用于颜色）
    rgb_img = Image.merge("RGB", (r, g, b))
    rgb_resized = rgb_img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
    rgb_array = np.array(rgb_resized)   # shape: (height, width, 3)

    # 4. 缩放 Alpha 掩码（最近邻插值保持二值性）
    alpha_mask_pil = Image.fromarray(alpha_mask.astype(np.uint8) * 255)
    alpha_resized = alpha_mask_pil.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
    alpha_resized = np.array(alpha_resized) > 128

    # 5. 生成字符画（每个字符覆盖上下两个像素）
    lines = []
    for y in range(0, pixel_height, 2):
        line_parts = []
        for x in range(pixel_width):
            top_alpha = alpha_resized[y, x]
            bottom_alpha = alpha_resized[y+1, x] if y+1 < pixel_height else False

            # 只有当上下两个像素都不透明时才绘制彩色块
            if not (top_alpha and bottom_alpha):
                line_parts.append("\033[0m ")
                continue

            top_color = tuple(rgb_array[y, x])
            bottom_color = tuple(rgb_array[y+1, x])

            # 构建 ANSI 颜色代码
            codes = []
            codes.append(f"\033[38;2;{top_color[0]};{top_color[1]};{top_color[2]}m")
            codes.append(f"\033[48;2;{bottom_color[0]};{bottom_color[1]};{bottom_color[2]}m")
            codes.append("▀")
            line_parts.append("".join(codes))

        lines.append("".join(line_parts) + "\033[0m")

    return lines