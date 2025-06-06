import requests

file_path = "/Users/nicolastabet/Downloads/test_audio.mp3"
url = "http://localhost:8000/process-audio/"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response JSON:")
print(response.json())
