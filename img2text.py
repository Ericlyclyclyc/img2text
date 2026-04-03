from colorblocks import image_to_color_blocks
from braille import image_to_braille
from asciichr import image_to_asciichr

if __name__ == "__main__":
    img_path = '1x.png'
    width = 50

    ascii_result = image_to_asciichr(
        image_path=img_path,
        output_width=width
    )
    color_blocks_result = image_to_color_blocks(
        image_path=img_path,
        output_width=width
    )
    braille_result = image_to_braille(
        image_path=img_path,
        output_width=width
    )
    for a, b, c in zip(ascii_result, color_blocks_result, braille_result):
        print(a + "   " + b + "   " + c)