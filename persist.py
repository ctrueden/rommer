import pickle 

def load(cachepath):
    try:
        with open(cachepath, 'rb') as cache:
            return pickle.load(cache)
    except:
        return {}

def save(cachepath, data):
    with open(cachepath, 'wb') as cache:
        pickle.dump(data, cache)
