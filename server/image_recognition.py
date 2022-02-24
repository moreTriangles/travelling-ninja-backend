import base64
from re import X
from matplotlib import image
import matplotlib
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw
from io import BytesIO, BufferedReader

api_url = 'https://api.api-ninjas.com/v1/imagetotext'
x_api_key = 'bHX2F/Str6Qo+AT8Cga0Lg==vqiiSWwHgXFs8pqK'
matplotlib.use('Agg')

def verify_AWB(file):
    image_file_descriptor = open(file, 'rb')
    files = {'image': image_file_descriptor}
    r = requests.post(api_url, headers={
        'X-Api-Key': x_api_key}, files=files)

    result = {'isValid': False,
              'output': "Warning: Our system cannot recognise the POD."}
    for i in r.json():
        if "Tracking Number" in i['text']:
            result['isValid'] = True
            result['output'] = "POD has been accepted!" + i['text']
            result['bounding_box'] = i['bounding_box']
            break

    plt.imshow(Image.open(file))
    plt.axis('off')
    if result['isValid']:
        width, height = Image.open(file).size
        x = result['bounding_box']['x1']*width
        y = result['bounding_box']['y1']*height
        w = result['bounding_box']['x2']*width - x
        h = result['bounding_box']['y2']*height - y
        plt.gca().add_patch(Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none'))
        myString = BytesIO()
        plt.savefig(myString, format='jpg')
        myString.seek(0)
        myStringBase64 = base64.b64encode(myString.read())
        result['img'] = myStringBase64.decode('utf-8')
    return result


def verify_location(file):
    image_file_descriptor = open(file, 'rb')
    files = {'image': image_file_descriptor}
    r = requests.post(api_url, headers={
        'X-Api-Key': x_api_key}, files=files)

    result = {'isValid': False,
              'output': "Warning: Our system cannot recognise the POD."}
    if r.json() != []:
        result['isValid'] = True
        result['output'] = "POD has been accepted!"
        result['bounding_box'] = r.json()[0]['bounding_box']

    plt.imshow(Image.open(file))
    plt.axis('off')
    if result['isValid']:
        width, height = Image.open(file).size
        x = result['bounding_box']['x1']*width
        y = result['bounding_box']['y1']*height
        w = result['bounding_box']['x2']*width - x
        h = result['bounding_box']['y2']*height - y
        rect = patches.Rectangle((x, y), w, h, linewidth=1,
                                 edgecolor='r', facecolor='none')
        plt.gca().add_patch(Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none'))
        myString = BytesIO()
        plt.savefig(myString, format='jpg')
        myString.seek(0)
        myStringBase64 = base64.b64encode(myString.read())
        result['img'] = myStringBase64.decode('utf-8')
    #plt.show()
    return result
