import argparse
import cv2
import numpy as np
import os
import pickle
import requests
from heaan import *
import math


def preprocess_image(context, image_path):
    """ preproces_image """
    dim = 1 << get_log_full_slots(context)

    image = cv2.imread(image_path)
    height, width, _ = image.shape
    path, _ = os.path.splitext(image_path)

    rgb_array = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(path + '-gray.jpg', rgb_array)

    ratio = math.sqrt((height * width) / dim)
    height = int(height / ratio)
    width = int(width / ratio)
    padding = dim - (height * width)

    resized = cv2.resize(rgb_array, (height, width))
    cv2.imwrite(path + '-resized.jpg', resized)

    flatten = np.array(resized).flatten()
    flatten = np.pad(flatten, (0, padding), 'constant', constant_values=0)
    return flatten, height, width


def postprocess_image(decrypted, height, width):
    """ postprocess_image """
    image = np.around(
        np.array(decrypted)[:height * width].reshape(height, width).astype(float))
    return image


def alice(
    input_path: str,
    parameter: str='FGb',
    host: str='localhost',
    port: int=5000
):
    """ client """
    # Specifying HEaaN parameter
    param = getattr(ParameterPreset, parameter)

    # Create HEaaN context
    context = make_context(param)

    # Generate client's secret key according to the context
    # and keep the key in the client's storage
    seckey = SecretKey(context)
    seckey.save('./secretkey.bin')

    # Container for public keys
    keypack = KeyPack(context)

    # KeyGenerator to generate public keys; encryption key and evaulation keys
    keygen = KeyGenerator(context, seckey, keypack)
    keygen.gen_enc_key()
    keygen.gen_mult_key()

    # Create container for data stream compatitable with native HEaaN library
    # and save KeyPack in it
    pubkeys = NativeStream()
    keypack.save(pubkeys)

    # Create encryptor
    encryptor = Encryptor(context)

    # Transform the given image into 1-dimensional numpy array
    flatten, height, width = preprocess_image(context, image_path=input_path)

    # Create a message container and fill it with the transformed image
    message = Message(flatten.astype(complex))

    # Create a ciphertext container and encrypt the message
    ciphertext = Ciphertext(context)
    encryptor.encrypt(message, keypack, ciphertext)

    # Container for data stream compatitable with native HEaaN library
    # and save the encrypted image in it
    userdata = NativeStream()
    ciphertext.save(userdata)

    # Server URL
    URL = f'http://{host}:{port}/heaan_service'
    # Serialize data and post it for outsourcing computations
    payload = pickle.dumps({
            'userdata' : userdata.bin,
            'parameter' : args.parameter,
            'pubkeys' : pubkeys.bin
    })
    response = requests.post(URL, data=payload)

    if response.status_code == 200:
        # Deserialize the reponse from server
        result = pickle.loads(response.content)

        # Create decryptor and decrypt the response using secret key
        decryptor = Decryptor(context)
        output = Message(get_log_full_slots(context))
        decryptor.decrypt(result, seckey, output)

        # Postprocess the output and save it as an image file
        processed_image = postprocess_image(output, height, width)
        cv2.imwrite(input_path + '-decrypted' + '.jpg', processed_image)
    else:
        print("Error occurred while sending the data structure")


# Run the client
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Alice\'s behavior')
    parser.add_argument('--input', '-in', type=str, required=True)
    parser.add_argument('--parameter', '-param', type=str, required=False, default='FGb')
    parser.add_argument('--host', type=str, required=False, default='localhost')
    parser.add_argument('--port', type=int, required=False, default=5000)
    args = parser.parse_args()
    
    alice(
        input_path=args.input,
        parameter=args.parameter,
        host=args.host,
        port=args.port
    )
