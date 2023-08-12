    # Open the image and resize/crop it
    with Image.open(BytesIO(file.body)) as image:
        # Resize the image if it's smaller than the desired size
        if image.width <= 800 and image.height <= 800:
            resized_image = image
        else:
            # Resize the image so that the shorter side is 800px
            size = (800, 800)
            image.thumbnail(size, Image.ANTIALIAS)
            resized_image = image

        # Crop the image to a 1:1 aspect ratio
        crop_size = min(resized_image.size)
        crop_box = ((resized_image.width - crop_size) // 2, (resized_image.height - crop_size) // 2,
                    (resized_image.width + crop_size) // 2, (resized_image.height + crop_size) // 2)
        cropped_image = resized_image.crop(crop_box)

        # Save the image to a buffer in JPEG format
        buffer = BytesIO()
        cropped_image.save(buffer, format='JPEG')
        buffer.seek(0)
