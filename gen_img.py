from PIL import Image

# Create a simple red test image
img = Image.new('RGB', (100, 100), color = 'red')
img.save('test_meal.jpg')
