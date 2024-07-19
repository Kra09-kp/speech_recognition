from flask import (Flask,
                   render_template,
                   request,
                   jsonify)
from pathlib import Path
from werkzeug.utils import secure_filename
from recogniser import predict,transcribe

app = Flask(__name__)

# Set upload folder
UPLOAD_FOLDER = Path('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


chat_history = [] # to maintain chat history
@app.route('/chat-history', methods=['GET'])
def get_chat_history():
    return jsonify(chat_history)

@app.route('/clear-history', methods=['POST'])
def clear_history():
    global chat_history
    chat_history = []
    return jsonify({'result': 'Chat history cleared'})


@app.route('/')
def index():
    clear_history()
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio_data' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['audio_data']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        filename = secure_filename(file.filename)
        file_path = app.config['UPLOAD_FOLDER'] / filename
        
        file.save(file_path)
        print(filename)
        
        
        # Process the uploaded file for prediction
        prediction = predict([filename])
        transcription = transcribe(file_path)
        response = f"{prediction}: "+ str(transcription)
        chat_history.append(response)
        # print(transcription)
        return jsonify({"result":response})



if __name__=='__main__':
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    app.run(debug=True)
    
