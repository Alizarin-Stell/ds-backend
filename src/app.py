from flask import Flask, jsonify, request
import logging
import requests
from io import BytesIO

from models.plate_reader import PlateReader
from image_provider_client import ImageProviderClient

plate_reader_model = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
image_client = ImageProviderClient('http://178.154.220.122:7777')

app = Flask(__name__)


@app.route('/')
def hello():
    return '<h1><center>Hello!</center></h1>'


@app.route('/recognize', methods=['POST'])
def recognize_plate():
    data = request.json
    img_id = data.get('img_id')
    if img_id is None:
        return jsonify({'error': 'No img_id provided'}), 400

    try:
        image_bytes = image_client.get_image(img_id)
        plate_text = plate_reader_model.read_text(image_bytes)
        return jsonify({'img_id': img_id, 'plate_text': plate_text})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to recognize plate', 'details': str(e)}), 500


@app.route('/recognize/multiple', methods=['POST'])
def recognize_multiple_plates():
    data = request.json
    img_ids = data.get('img_ids')
    if not img_ids:
        return jsonify({'error': 'No img_ids provided'}), 400

    results = []
    for img_id in img_ids:
        try:
            image_bytes = image_client.get_image(img_id)
            plate_text = plate_reader_model.read_text(image_bytes)
            results.append({'img_id': img_id, 'plate_text': plate_text})
        except ValueError as e:
            results.append({'img_id': img_id, 'error': 'Failed to download image', 'details': str(e)})
        except Exception as e:
            results.append({'img_id': img_id, 'error': 'Failed to recognize plate', 'details': str(e)})

    return jsonify(results)


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.run(host='0.0.0.0', port=8080, debug=True)
