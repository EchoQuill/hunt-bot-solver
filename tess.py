import glob
import os
import requests
from PIL import Image
import numpy
import io

# Define priority groups based on your folder structure
priority_groups = [
    list("abdegkmpqstvwxyz"),  # First priority
    list("fho"),               # Second priority
    list("cnru"),              # Third priority
    list("jl"),                # Fourth priority
    list("i"),                 # Fifth priority
]

def solve_huntbot_captcha(captcha_url):
    checks = []
    check_images = glob.glob("corpus/*.png")

    # Sort images based on the defined priority groups
    for priority_group in priority_groups:
        for check_image in sorted(check_images):
            letter = check_image.split(".")[0].split(os.sep)[-1]
            if letter in priority_group:
                img = Image.open(check_image)
                checks.append((img, img.size, letter))

    # Fetching the captcha image using requests
    resp = requests.get(captcha_url)
    large_image = Image.open(io.BytesIO(resp.content))
    large_array = numpy.array(large_image)

    matches = []
    for img, (small_w, small_h), letter in checks:
        small_array = numpy.array(img)
        mask = small_array[:, :, 3] > 0
        for y in range(large_array.shape[0] - small_h + 1):
            for x in range(large_array.shape[1] - small_w + 1):
                segment = large_array[y:y + small_h, x:x + small_w]
                if numpy.array_equal(segment[mask], small_array[mask]):
                    if not any((m[0] - small_w < x < m[0] + small_w) and (m[1] - small_h < y < m[1] + small_h) for m in matches):
                        matches.append((x, y, letter))

    matches = sorted(matches, key=lambda tup: tup[0])
    return "".join([i[2] for i in matches])

# Example usage:
captcha_url = "https://cdn.discordapp.com/attachments/989702680911954010/1287007385730158664/captcha.png?ex=66effa88&is=66eea908&hm=cd92824ca3aa418ed1cb7cdea74fb3c18f9b3b2d8410ac6a1ddd91fdb213e694&"
captcha_solution = solve_huntbot_captcha(captcha_url)
print("Captcha solution:", captcha_solution)
