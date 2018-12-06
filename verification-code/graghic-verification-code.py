import tesserocr
from PIL import Image


# image = Image.open('../data/code.jpg')
# result = tesserocr.image_to_text(image)
# print(result)

# print(tesserocr.file_to_text('../data/code.jpg'))


image = Image.open('../data/code2.jpg')
image = image.convert('L')
threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)
image = image.point(table, '1')
image.show()
result = tesserocr.image_to_text(image)
print(result)


