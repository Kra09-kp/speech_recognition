from tensorflow.keras.models import load_model # type: ignore
import numpy as np # type: ignore
import librosa # type: ignore
from pathlib import Path
from joblib import load # type: ignore
import pandas as pd # type: ignore
import requests

with open('hugging_face_api_key.txt', 'r') as file:
    api_key = file.read()

scaler = load('./model/scaler.pkl')
model = load_model('./model/voice_model.h5')


# extract the feature of audio file

def extract_features(files):
    print("Extracting features")
    # Sets the name to be the path to where the file is in my computer
    folder = Path('E:/DeepLearning/speech_recognition/uploads').resolve()
    file_name = folder / files.file
    

    # Loads the audio file as a floating point time series and assigns the default sample rate
    # Sample rate is set to 22050 by default
    X, sample_rate = librosa.load(file_name) 

    # Generate Mel-frequency cepstral coefficients (MFCCs) from a time series 
    mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T,axis=0)

    # Generates a Short-time Fourier transform (STFT) to use in the chroma_stft
    stft = np.abs(librosa.stft(X))

    # Computes a chromagram from a waveform or power spectrogram.
    chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)

    # Computes a mel-scaled spectrogram.
    mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T,axis=0)

    # Computes spectral contrast
    contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)

    # Computes the tonal centroid features (tonnetz)
    tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X),
    sr=sample_rate).T,axis=0)
        

    return mfccs, chroma, mel, contrast, tonnetz

def create_features(features_label):
    print("Creating Features")
    features = []
    for i in range(0, len(features_label)):
        features.append(np.concatenate((features_label[i][0], features_label[i][1], 
                    features_label[i][2], features_label[i][3],
                    features_label[i][4]), axis=0))
    return features


def process_test(test):
    print("processing test")
    test = pd.DataFrame(test, columns=['file'])
    test = test.apply(extract_features, axis=1)
    test = np.array(test)
    test = create_features(test)
    test = np.array(test)
    test = scaler.transform(test)
    return test

def label_prediction(x):
    print("labeling prediction")
    if x > 0.5:
        return 'AI'
    else:
        return 'Person'
    
def predict(test):
    print("predicting")
    test = process_test(test)
    pred = model.predict(test)
    pred = label_prediction(pred)
    print("Prediction Completed !",pred)
    
    return pred


def transcribe(filename):
    print("Transcribing audio...")
    API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"
    headers = {"Authorization": api_key}
    with open(filename, 'rb') as f:
        data = f.read()
    
    response = requests.post(API_URL, headers=headers, data=data)
    
    try:
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        print("Transcription completed!")
        # print(response)
        print(response.json()['text'])
        return response.json()['text']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")
    except ValueError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response content: {response.text}")
    
    return "Sorry, I couldn't transcribe the audio file. Please try again later."