from PIL import Image, ImageFilter
import io

def blur_images_in_presentation(presentation,user_inp):
    mask_color = (0, 0, 0)
    for slide in presentation.slides:
        for shape in list(slide.shapes):
            if shape.shape_type == 13:  # Check if shape is Picture
                image = Image.open(io.BytesIO(shape.image.blob))
                
                if user_inp=='y':
                    width, height = image.size
                    blurred_image = Image.new('RGB', (width, height), mask_color)
                else:
                    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=15))
                blurred_image_bytes = io.BytesIO()
                blurred_image.save(blurred_image_bytes, format='PNG')
                blurred_image_bytes.seek(0)
                left = shape.left
                top = shape.top
                width = shape.width
                height = shape.height
                slide.shapes._spTree.remove(shape._element)
                slide.shapes.add_picture(blurred_image_bytes, left, top, width, height)
