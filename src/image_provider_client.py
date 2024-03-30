import requests
from io import BytesIO

class ImageProviderClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url
        self.timeout = timeout

    def get_image(self, img_id):
        try:
            response = requests.get(f'{self.base_url}/images/{img_id}', timeout=self.timeout)
            response.raise_for_status()
            return BytesIO(response.content)
        except requests.RequestException as e:
            raise ValueError(f'Failed to download image with ID {img_id}: {e}') from e