from flask import Flask, request
import argparse
import pickle
from heaan import *


app = Flask(__name__)


def bob(client_data):
    """
    bob
    @client_data:
    """
    try:
        payload = pickle.loads(request.get_data())
    except pickle.UnpicklingError as err:
        raise f'Failed to deserialize the data: {err}'

    # Create HEaaN context at server side according to the given parameter
    param = getattr(ParameterPreset, payload['parameter'])
    context = make_context(param)

    # Create encryptor, keypack container
    encryptor = Encryptor(context)
    keypack = KeyPack(context)

    # NativeStream container reusable within the entire scope
    stream = NativeStream()

    # Align keypack with client's public keys
    stream.load(payload['pubkeys'])
    print(bytes(payload['pubkeys'], 'utf-8')[:10])
    print(stream.bin[:10])
    keypack.load(stream)

    # Create HomEvaluator container for server side computations
    evaluator = HomEvaluator(context, keypack)

    # Create a sample filter for processing the image user encrypted
    message = Message(get_log_full_slots(context))
    message.fill(0.7)
    filter = Ciphertext(context)
    encryptor.encrypt(message, keypack, filter)

    # Create a ciphertext container and deserialize userdata in it
    stream.clear().load(payload['pubkeys'])
    userdata = Ciphertext(context).load(stream)

    # Create the result ciphertext container and process userdata ciphertext
    result = Ciphertext(context)
    evaluator.mult(userdata, filter, result)

    # Save result ciphertext in the existing stream container
    stream.clear()
    result.save(stream)
    return pickle.dumps(result)


@app.route('/heaan_service', methods=['POST'])
def heaan_service():
    """ heaan_service """
    result = bob(request.get_data())
    return result


if __name__ == '__main__':
    app.run()
