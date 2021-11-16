from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
import requests

from torchvision.datasets import CIFAR10


def main():

	dataset = CIFAR10("../datasets/")

	url = 'http://images.cocodataset.org/val2017/000000039769.jpg'
	image = Image.open(requests.get(url, stream=True).raw)

	feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
	model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

	inputs = feature_extractor(images=image, return_tensors="pt")
	outputs = model(**inputs)
	logits = outputs.logits
	# model predicts one of the 1000 ImageNet classes
	predicted_class_idx = logits.argmax(-1).item()
	print("Predicted class:", model.config.id2label[predicted_class_idx])


if __name__ == "__main__":
	main()