from nexora.ml.train import Predictor

# Global predictor instance used by the edge service
predictor = None

def get_predictor():
    return predictor

def set_predictor(p):
    global predictor
    predictor = p

def init_predictor():
    global predictor
    try: 
        predictor = Predictor()
    except FileNotFoundError: 
        predictor = None
