import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from scipy.ndimage import gaussian_filter

def image_to_braille(
    image_path: str,
    output_width: int = 80,
    sharpen_strength: float = 1.2,
    contrast_factor: float = 1.5,
    sigma: float = 3.0,
    k: float = 0.4,
    alpha_threshold: int = 128
) -> str:
    """
    将图片转换为彩色盲文字符画，透明区域不显示任何点阵，每个字符带有对应区域的平均颜色

    参数:
        image_path: 图片路径（支持透明 PNG）
        output_width: 输出字符宽度（盲文字符个数）
        sharpen_strength: 锐化强度（1.0=无变化，大于1增强）
        contrast_factor: 对比度增强因子（1.0=不变）
        sigma: 高斯滤波的sigma（控制局部区域大小）
        k: 阈值偏移系数（threshold = local_mean - k * local_std）
        alpha_threshold: Alpha 通道阈值，低于此值视为透明（0~255）
    """
    # 1. 打开图片，保留 Alpha 通道
    img = Image.open(image_path).convert('RGBA')
    r, g, b, a = img.split()
    alpha_mask = np.array(a) > alpha_threshold

    # 2. 转为灰度图用于自适应阈值
    gray_img = Image.merge('RGB', (r, g, b)).convert('L')

    # 3. 边缘增强：锐化 + 对比度
    if sharpen_strength != 1.0:
        gray_img = gray_img.filter(ImageFilter.UnsharpMask(radius=1, percent=int(100 * (sharpen_strength - 1))))
    if contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(gray_img)
        gray_img = enhancer.enhance(contrast_factor)

    # 4. 计算目标像素尺寸（盲文宽 = output_width，每个盲文字符宽2像素，高4像素）
    pixel_width = output_width * 2
    pixel_height = int((pixel_width * gray_img.height) / gray_img.width)
    pixel_height = ((pixel_height + 3) // 4) * 4   # 调整为4的倍数

    # 5. 缩放灰度图（用于二值化）
    gray_resized = gray_img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)

    # 6. 缩放 RGB 原图（用于取色）
    rgb_img = Image.merge('RGB', (r, g, b))
    rgb_resized = rgb_img.resize((pixel_width, pixel_height), Image.Resampling.LANCZOS)
    rgb_array = np.array(rgb_resized)  # shape: (height, width, 3)

    # 7. 缩放 Alpha 掩码（最近邻插值保持二值性）
    alpha_mask_pil = Image.fromarray(alpha_mask.astype(np.uint8) * 255)
    alpha_mask_resized = alpha_mask_pil.resize((pixel_width, pixel_height), Image.Resampling.NEAREST)
    alpha_mask_resized = np.array(alpha_mask_resized) > 128

    # 8. 灰度图转为 numpy 数组，进行自适应阈值
    arr = np.array(gray_resized, dtype=np.float32)
    local_mean = gaussian_filter(arr, sigma=sigma)
    local_std = np.sqrt(gaussian_filter((arr - local_mean) ** 2, sigma=sigma))
    threshold = local_mean - k * local_std
    bw = (arr < threshold).astype(np.uint8) * 255   # 暗部为0，亮部为255

    # 9. 生成彩色盲文字符画
    h, w = bw.shape
    braille_lines = []
    # 盲文点阵映射：2x4 网格 -> Unicode 位索引
    dot_map = [
        (0, 0), (2, 0), (0, 1), (2, 1),
        (1, 0), (3, 0), (1, 1), (3, 1)
    ]

    for y in range(0, h, 4):
        line_parts = []
        for x in range(0, w, 2):
            # 检查当前 2x4 块是否主要为透明
            block_alpha = alpha_mask_resized[y:y+4, x:x+2]
            if block_alpha.size == 0 or np.sum(block_alpha) < 4:   # 少于4个不透明像素视为透明
                line_parts.append("\033[0m ")   # 重置颜色 + 空格（完全透明）
                continue

            # 计算当前块的平均 RGB 颜色（仅使用不透明像素）
            block_rgb = rgb_array[y:y+4, x:x+2, :]   # (4,2,3)
            # 只取不透明像素的平均值
            alpha_block = alpha_mask_resized[y:y+4, x:x+2]
            if np.sum(alpha_block) > 0:
                # 提取不透明像素的颜色
                opaque_colors = block_rgb[alpha_block]
                avg_color = np.mean(opaque_colors, axis=0).astype(int)
            else:
                avg_color = (128, 128, 128)  # fallback，实际上不会进入这里

            # 生成盲文点阵掩码
            mask = 0
            for bit, (dy, dx) in enumerate(dot_map):
                ny, nx = y + dy, x + dx
                if ny < h and nx < w and bw[ny, nx] == 0 and alpha_mask_resized[ny, nx]:
                    mask |= (1 << bit)

            # 构建带颜色的盲文字符
            if mask == 0:
                # 为保持颜色一致性，仍输出重置后的空格
                line_parts.append("\033[0m ")
            else:
                braille_char = chr(0x2800 + mask)
                # 设置前景色，不设置背景色（使用终端默认背景）
                colored_char = f"\033[38;2;{avg_color[0]};{avg_color[1]};{avg_color[2]}m{braille_char}"
                line_parts.append(colored_char)

        # 行末重置样式并换行
        lines = "".join(line_parts) + "\033[0m"
        braille_lines.append(lines)

    return braille_lines