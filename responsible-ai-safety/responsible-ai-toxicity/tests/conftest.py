import sys
import types
import numpy as np

# Ensure src is importable
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# --- Stub tensorflow / keras / tensorflow_hub to avoid import-time model loads in tests ---
import types as _types
tensorflow_mod = _types.ModuleType('tensorflow')

# Provide a minimal keras.models.load_model that returns a dummy model with predict()
class _DummyModel:
    def predict(self, x):
        import numpy as _np
        # return a single prediction vector of length 5 (matches labels used in videonsfw)
        return _np.array([[0.0, 0.0, 0.0, 0.0, 0.0]])

class _DummyKerasModels:
    @staticmethod
    def load_model(path, custom_objects=None, compile=True):
        return _DummyModel()

keras_mod = _types.ModuleType('keras')
keras_models_mod = _types.ModuleType('keras.models')
keras_models_mod.load_model = _DummyKerasModels.load_model
keras_mod.models = keras_models_mod

# Attach keras under tensorflow so 'from tensorflow import keras' works
tensorflow_mod.keras = keras_mod

# Minimal tensorflow_hub with KerasLayer symbol used by videonsfw
hub_mod = _types.ModuleType('tensorflow_hub')
class _DummyKerasLayer:
    def __init__(self, *a, **k):
        pass
hub_mod.KerasLayer = _DummyKerasLayer

# Register stubs in sys.modules before tests import src
sys.modules['tensorflow'] = tensorflow_mod
sys.modules['keras'] = keras_mod
sys.modules['keras.models'] = keras_models_mod
sys.modules['tensorflow_hub'] = hub_mod

# --- end stubs ---

# --- Stub transformers (pipeline, AutoModelForSequenceClassification, AutoTokenizer) ---
transformers_mod = _types.ModuleType('transformers')

def fake_pipeline(task=None, model=None, tokenizer=None, **kwargs):
    # returns a callable that echoes input into a classification-like response
    def _call(urls):
        # Return for each url a list of label/score dicts; tests will monkeypatch as needed
        return [[{"label": "benign", "score": 0.1}] for _ in urls]
    return _call

class FakeAutoModel:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return object()

class FakeAutoTokenizer:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return object()

transformers_mod.pipeline = fake_pipeline
transformers_mod.AutoModelForSequenceClassification = FakeAutoModel
transformers_mod.AutoTokenizer = FakeAutoTokenizer
sys.modules['transformers'] = transformers_mod

# --- end transformers stubs ---

# Minimal torch stub
torch_mod = types.ModuleType('torch')
class FakeTensor:
    def __init__(self, arr):
        self._arr = np.array(arr)
    def cpu(self):
        return self
    def numpy(self):
        return self._arr
class FakeOutputs:
    def __init__(self, arr):
        self.logits = FakeTensor(arr)
class FakeNNFunctional:
    @staticmethod
    def softmax(logits, dim=-1):
        return logits
class FakeNoGrad:
    def __enter__(self):
        return None
    def __exit__(self, exc_type, exc, tb):
        return False
torch_mod.nn = types.SimpleNamespace(functional=FakeNNFunctional)
torch_mod.no_grad = lambda: FakeNoGrad()
# Minimal cuda/device support expected by malicious_url_service
class _FakeDevice:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"_FakeDevice({self.name})"

cuda_ns = types.SimpleNamespace(is_available=lambda: False)
torch_mod.cuda = cuda_ns
torch_mod.device = lambda name: _FakeDevice(name)
sys.modules['torch'] = torch_mod

# Minimal transformers stub
transformers_mod = types.ModuleType('transformers')
class FakeModel:
    def __call__(self, **inputs):
        return FakeOutputs([[0.1,0.2,0.3,0.15,0.25]])
class FakeExtractor:
    def __call__(self, images, return_tensors=None):
        return {'pixel_values': None}
class FakeAutoModel:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return FakeModel()
class FakeAutoFeatureExtractor:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return FakeExtractor()
transformers_mod.AutoModelForImageClassification = FakeAutoModel
transformers_mod.AutoFeatureExtractor = FakeAutoFeatureExtractor
# also expose pipeline and sequence-classification API used by malicious_url_service
transformers_mod.pipeline = lambda task=None, model=None, tokenizer=None, **kwargs: (lambda urls: [[{"label": "benign", "score": 0.1}] for _ in urls])

# Provide a lightweight sequence-classification model stub with .to()
class _FakeSeqModel:
    def __init__(self):
        pass
    def to(self, device):
        return self

class _FakeSeqAutoModel:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return _FakeSeqModel()

class _FakeSeqAutoTokenizer:
    @staticmethod
    def from_pretrained(path, local_files_only=True):
        return object()

transformers_mod.AutoModelForSequenceClassification = _FakeSeqAutoModel
transformers_mod.AutoTokenizer = _FakeSeqAutoTokenizer
# provide configuration_utils submodule expected by sentence_transformers
cfg_mod = types.ModuleType('transformers.configuration_utils')
cfg_mod.PretrainedConfig = object
sys.modules['transformers.configuration_utils'] = cfg_mod
sys.modules['transformers'] = transformers_mod

# Minimal sentence_transformers stub (provide backend.load names)
st_mod = types.ModuleType('sentence_transformers')
backend_mod = types.ModuleType('sentence_transformers.backend')
load_mod = types.ModuleType('sentence_transformers.backend.load')
def load_onnx_model(*args, **kwargs):
    return None
def load_openvino_model(*args, **kwargs):
    return None
load_mod.load_onnx_model = load_onnx_model
load_mod.load_openvino_model = load_openvino_model
sys.modules['sentence_transformers'] = st_mod
sys.modules['sentence_transformers.backend'] = backend_mod
sys.modules['sentence_transformers.backend.load'] = load_mod
class DummySentenceTransformer:
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return None
    def encode(self, *args, **kwargs):
        return np.zeros((1,384))

# expose SentenceTransformer symbol expected by imports
st_mod.SentenceTransformer = DummySentenceTransformer

# Minimal faiss stub
sys.modules['faiss'] = types.ModuleType('faiss')

# Minimal cv2 stub
cv2_mod = types.ModuleType('cv2')
def imencode(ext, frame):
    return True, b'JPEGBYTES'
class DummyVideoCapture:
    def __init__(self, url):
        self._opened = False if (url and 'bad' in str(url)) else True
        self._read_count = 0
    def read(self):
        import numpy as _np
        if not self._opened:
            return False, None
        if self._read_count == 0:
            self._read_count += 1
            frame = _np.zeros((480,640,3), dtype=_np.uint8)
            return True, frame
        return False, None
    def isOpened(self):
        return self._opened
    def release(self):
        return
cv2_mod.VideoCapture = DummyVideoCapture
cv2_mod.imencode = imencode
cv2_mod.cvtColor = lambda frame, code: frame
cv2_mod.resize = lambda frame, size: frame
cv2_mod.GaussianBlur = lambda img, ksize, sigma: img
cv2_mod.putText = lambda *a, **k: None
cv2_mod.COLOR_BGR2RGB = 0
cv2_mod.FONT_HERSHEY_SIMPLEX = 0
sys.modules['cv2'] = cv2_mod

# Add commonly used cv2 functions/attributes that some modules expect
def imdecode(arr, flag):
    import numpy as _np
    # return a small dummy image
    return _np.zeros((50, 50, 3), dtype=_np.uint8)

def imwrite(path, img):
    # write a small placeholder so functions that delete the file later work
    with open(path, 'wb') as _f:
        _f.write(b'DUMMY')
    return True

class DummyVideoWriter:
    def __init__(self, *args, **kwargs):
        self._frames = []
    def write(self, frame):
        self._frames.append(frame)
    def release(self):
        return

cv2_mod.imdecode = imdecode
cv2_mod.imwrite = imwrite
cv2_mod.VideoWriter = DummyVideoWriter
cv2_mod.VideoWriter_fourcc = lambda *args: 0
cv2_mod.COLOR_RGB2BGR = 0
cv2_mod.CAP_PROP_FRAME_WIDTH = 3
cv2_mod.CAP_PROP_FRAME_HEIGHT = 4
cv2_mod.CAP_PROP_FPS = 5

# Minimal nudenet stub to avoid import-time model loads
import types as _types
class _DummyNudeDetector:
    def __init__(self, *a, **k):
        pass
    def detect(self, path):
        return []
sys.modules['nudenet'] = _types.SimpleNamespace(NudeDetector=_DummyNudeDetector)

# Minimal detoxify and toxicModel stubs
detox_mod = types.ModuleType('detoxify')
class DummyDetox:
    def __init__(self, *args, **kwargs):
        pass
    def predict(self, text):
        return {'toxicity': 0.0, 'severe_toxicity':0.0,'obscene':0.0,'threat':0.0,'insult':0.0,'identity_attack':0.0,'sexual_explicit':0.0}
detox_mod.Detoxify = DummyDetox
sys.modules['detoxify'] = detox_mod

toxic_mod = types.ModuleType('toxicModel')
class DummyToxic:
    def analyze(self, text):
        return {'toxicity': 0.0}
toxic_mod.Toxic = DummyToxic
toxic_mod.toxicityModel = types.SimpleNamespace(predict=lambda text: {'toxicity':0.0,'severe_toxicity':0.0,'obscene':0.0,'threat':0.0,'insult':0.0,'identity_attack':0.0,'sexual_explicit':0.0})
sys.modules['toxicModel'] = toxic_mod
