from flask import Flask, request, jsonify
import torch
from cnn_model import CNN
from Shape_Detection import save_image_to_binary, prepare_image
import os

app = Flask(__name__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = CNN()
model.to(device)
model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    temp_path = os.path.join('temp', file.filename)
    file.save(temp_path)
    image = prepare_image(temp_path)
    image = image.unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output.data, 1)
    
    os.remove(temp_path)
    
    label_map = {0: "circle", 1: "halfmoon", 2: "heart", 3: "square", 4: "star", 5: "triangle"}
    predicted_label = label_map[predicted.item()]
    
    return jsonify({'predicted_class': predicted_label})

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(host='0.0.0.0', port=5000)
