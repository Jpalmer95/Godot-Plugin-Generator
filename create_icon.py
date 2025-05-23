from PIL import Image, ImageDraw, ImageFont

try:
    # Try to load a common sans-serif font.
    # On many systems, "DejaVuSans" is available. If not, Pillow's default will be used.
    font = ImageFont.truetype("DejaVuSans.ttf", 12) 
except IOError:
    # If the specific font is not found, use Pillow's default font
    font = ImageFont.load_default()

# Create a 16x16 image with a light gray background
img = Image.new('RGB', (16, 16), color = (200, 200, 200))
d = ImageDraw.Draw(img)

# Text to draw and its color
text = "P"
text_color = (50, 50, 50) # Dark Gray

# Calculate text size and position for centering
# For Pillow versions < 10.0.0, use textsize
# For Pillow versions >= 10.0.0, use textbbox and then calculate width/height
try:
    # Pillow >= 10.0.0
    bbox = d.textbbox((0, 0), text, font=font)
    textwidth = bbox[2] - bbox[0]
    textheight = bbox[3] - bbox[1]
    x = (16 - textwidth) / 2
    y = (16 - textheight) / 2
except AttributeError:
    # Pillow < 10.0.0
    textwidth, textheight = d.textsize(text, font=font)
    x = (16 - textwidth) / 2
    y = (16 - textheight) / 2


# Draw the text. Adjust y-offset slightly if needed for better visual centering.
# The y position might need slight adjustment as text rendering isn't always perfectly centered from baseline.
d.text((x, y - 1), text, fill=text_color, font=font)

# Save the image
img.save('default_icon.png')
print("default_icon.png created successfully.")
