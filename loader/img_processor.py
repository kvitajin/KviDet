from torchvision import transforms
from PIL.Image import Image

import config


def resize_image(image: Image, max_size: int = config.IMG_TARGET_SIZE):
    ratio = min(max_size / image.width, max_size / image.height)
    imw = round(image.width * ratio)
    imh = round(image.height * ratio)
    pad_side = max(int((imh - imw) / 2), 0)
    pad_vertex = max(int((imw - imh) / 2), 0)
    img_transforms = transforms.Compose([transforms.Resize((imh, imw)),
                                         transforms.Pad((pad_side, pad_vertex), (128, 128, 128)),
                                         ])

    return img_transforms(image)


def prepare_image_for_torch(image: Image, max_size: int = config.IMG_TARGET_SIZE):
    resized_image = resize_image(image, max_size)
    image_as_tensor = transforms.ToTensor()(resized_image)

    return image_as_tensor.float().unsqueeze_(0)
