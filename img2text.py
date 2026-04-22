import click
from colorblocks import image_to_color_blocks
from braille import image_to_braille
from asciichr import image_to_asciichr

@click.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('-w', '--width', default=50, type=int, help='输出宽度（字符数）')
@click.option('-a', '--alpha_threshold', default=128, type=int, help='Alpha 通道阈值，低于此值视为透明 (0-255)')
@click.option('-c', '--colored', is_flag=True, default=False, help='启用 ANSI 颜色代码输出')
def main(image_path, width, alpha_threshold, colored):
    """
    将图片转换为三种风格的彩色字符画（ASCII、盲文、半色块）。
    透明区域自动替换为空格。
    """
    ascii_result = image_to_asciichr(
        image_path=image_path,
        output_width=width,
        alpha_threshold=alpha_threshold,
        colored=colored
    )
    braille_result = image_to_braille(
        image_path=image_path,
        output_width=width,
        alpha_threshold=alpha_threshold,
        colored=colored
    )
    color_blocks_result = image_to_color_blocks(
        image_path=image_path,
        output_width=width,
        alpha_threshold=alpha_threshold,
        colored=colored
    )

    # 终端并排显示三种结果
    for a, b, c in zip(ascii_result, braille_result, color_blocks_result):
        print(a + "   " + b + "   " + c)

    # 保存到文件
    with open('a.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(ascii_result))
    with open('b.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(braille_result))
    with open('c.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(color_blocks_result))

if __name__ == '__main__':
    main()