"""Tests for `service.healthcheck_service.model_health`.

These tests isolate the healthcheck service and replace its `health_check_functions`
with deterministic stubs to exercise:
  * Argument routing / payload selection logic per function name
  * Success path (all functions succeed -> status 'healthy', empty unhealthy list)
  * Failure path (one or more functions raise -> status 'unhealthy', names recorded)
  * Multiple failures accumulate
  * Global state (`status`, `unhealthy_checks`) reset between test runs via fixture

Service logic summary:
  - For each callable in `health_check_functions`, payload variant chosen by `__name__`
    plus a special case for Gibberish bound method (func.__name__ == 'scan' and
    func.__self__.__class__.__name__ == 'Gibberish').
  - Returns (status, unhealthy_checks) after parallel execution.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from tests.utils.mock_helpers import (
    make_aicloud_modules,
    make_local_constants,
    isolate_and_reload,
    make_config_logger_stub,
)
from tests.utils.isolate_module import reload_module

# --- Test Fixtures ---

@pytest.fixture(scope='function')
def health_mod():
    """Reload healthcheck service in isolated module context and reset globals.

    Yields the reloaded module while the isolation context is active so monkeypatching
    affects the live module and imported service references do not leak.
    """
    # Build lightweight stub modules for all dependencies imported by healthcheck_service
    import types as _types
    # Stub service modules providing required symbols only
    svc_bancode = _types.ModuleType('service.bancode_service')
    class _BanCode:
        def scan(self, payload):
            return {'result': [], 'time_taken': '0s'}
    svc_bancode.BanCode = _BanCode

    svc_detox = _types.ModuleType('service.detoxifyModel')
    def toxicity_check(payload, id):
        return {'result': [], 'time_taken': '0s'}
    svc_detox.toxicity_check = toxicity_check

    svc_embed = _types.ModuleType('service.EmbedingModel')
    def multi_q_net_embedding(id, text):
        return {'result': [], 'time_taken': '0s'}
    svc_embed.multi_q_net_embedding = multi_q_net_embedding

    svc_gib = _types.ModuleType('service.gibberish_service')
    class _Gibberish:
        def scan(self, payload):
            return {'result': [], 'time_taken': '0s'}
    svc_gib.Gibberish = _Gibberish

    svc_inj = _types.ModuleType('service.injectionModel')
    def promptInjection_check(text, id):
        return {'result': [], 'time_taken': '0s'}
    svc_inj.promptInjection_check = promptInjection_check

    svc_priv = _types.ModuleType('service.privacyModel')
    def privacy(id, text):
        return {'result': [], 'time_taken': '0s'}
    svc_priv.privacy = privacy

    svc_topic = _types.ModuleType('service.topicModel')
    def restricttopic_check(payload, id):
        return {'result': [], 'time_taken': '0s'}
    svc_topic.restricttopic_check = restricttopic_check

    svc_translate = _types.ModuleType('service.translateservice')
    def translate_to_english(text):
        return {'result': [], 'time_taken': '0s'}
    svc_translate.translate_to_english = translate_to_english

    # Minimal external library stubs (only if some service module code path tries to import them before we replace list)
    tr = _types.ModuleType('transformers'); tr.pipeline = lambda *a, **k: (lambda x: [])
    torch_stub = _types.ModuleType('torch'); torch_stub.cuda = _types.SimpleNamespace(is_available=lambda: False)
    st = _types.ModuleType('sentence_transformers')
    class SentenceTransformer:  # pragma: no cover - simple stub
        def encode(self, text): return [0.0]
    st.SentenceTransformer = SentenceTransformer
    st.util = _types.SimpleNamespace(cos_sim=lambda a, b: 0.5)

    replacements = {
        **make_aicloud_modules(),
        'constants.local_constants': make_local_constants(),
        'config.logger': make_config_logger_stub(),  # lightweight logger
        # service module stubs
        'service.bancode_service': svc_bancode,
        'service.detoxifyModel': svc_detox,
        'service.EmbedingModel': svc_embed,
        'service.gibberish_service': svc_gib,
        'service.injectionModel': svc_inj,
        'service.privacyModel': svc_priv,
        'service.topicModel': svc_topic,
        'service.translateservice': svc_translate,
        # external libs stubs
        'transformers': tr,
        'torch': torch_stub,
        'sentence_transformers': st,
    }
    # ensure a clean import each test
    import sys as _sys
    _sys.modules.pop('service.healthcheck_service', None)
    with isolate_and_reload('service.healthcheck_service', replacements):
        mod = reload_module('service.healthcheck_service')
        # Reset global state that the service mutates
        if hasattr(mod, 'unhealthy_checks'):
            mod.unhealthy_checks = []
        if hasattr(mod, 'status'):
            mod.status = 'healthy'
        yield mod


def _make_call_recorder(name, raise_exc=False):
    """Return a stub function with the given __name__ that records its call args."""
    def stub(*args, **kwargs):
        calls[name] = {'args': args, 'kwargs': kwargs}
        if raise_exc:
            raise Exception('boom')
        return True
    stub.__name__ = name
    return stub


class _FakeGib:
    def scan(self, payload):  # legacy unused after replacing with real-named class
        calls['scan'] = {'args': (payload,), 'kwargs': {}}
        return True


def _install_stub_list(mod, fail_names=None):
    """Replace mod.health_check_functions with controlled stubs.

    fail_names: iterable of function names that should raise an exception when called.
    Includes a bound method stub for Gibberish (name-based special case logic).
    """
    if fail_names is None:
        fail_names = set()
    # shared record dict
    global calls
    calls = {}
    # Create a class literally named Gibberish so healthcheck_service special case matches
    class Gibberish:
        def scan(self, payload):
            calls['scan'] = {'args': (payload,), 'kwargs': {}}
            if 'scan' in fail_names:
                raise Exception('boom')
            return True

    stub_funcs = [
        _make_call_recorder('toxicity_check', 'toxicity_check' in fail_names),
        _make_call_recorder('multi_q_net_embedding', 'multi_q_net_embedding' in fail_names),
        Gibberish().scan,  # bound method triggers gibberish_payload routing
        _make_call_recorder('promptInjection_check', 'promptInjection_check' in fail_names),
        _make_call_recorder('privacy', 'privacy' in fail_names),
        _make_call_recorder('restricttopic_check', 'restricttopic_check' in fail_names),
        _make_call_recorder('translate_to_english', 'translate_to_english' in fail_names),
        _make_call_recorder('bancode_scan', 'bancode_scan' in fail_names),  # default payload branch
    ]
    mod.health_check_functions = stub_funcs
    return calls


# --- Tests ---

def test_model_health_all_success(health_mod):
    rec = _install_stub_list(health_mod)
    status, unhealthy = health_mod.model_health()
    assert status == 'healthy'
    assert unhealthy == []
    # Verify argument routing logic per function name
    # toxicity_check(payload, id)
    tox_args = rec['toxicity_check']['args']
    assert len(tox_args) == 2 and isinstance(tox_args[0], dict) and isinstance(tox_args[1], str)
    # multi_q_net_embedding(id, text)
    embed_args = rec['multi_q_net_embedding']['args']
    assert len(embed_args) == 2 and isinstance(embed_args[0], str) and isinstance(embed_args[1], str)
    # Gibberish scan gets gibberish_payload dict with labels
    gib_payload = rec['scan']['args'][0]
    assert isinstance(gib_payload, dict) and 'labels' in gib_payload and 'text' in gib_payload
    # default branch (BanCode placeholder) should have received the generic payload dict with 'text'
    default_payload = rec['bancode_scan']['args'][0]
    assert isinstance(default_payload, dict) and default_payload.get('text') == 'Ping'
    # promptInjection_check(text, id)
    inj_args = rec['promptInjection_check']['args']
    assert len(inj_args) == 2 and isinstance(inj_args[0], str) and isinstance(inj_args[1], str)
    # privacy(id, text)
    priv_args = rec['privacy']['args']
    assert len(priv_args) == 2 and isinstance(priv_args[0], str) and isinstance(priv_args[1], str)
    # restricttopic_check(restricted_topic_payload, id)
    rt_args = rec['restricttopic_check']['args']
    assert len(rt_args) == 2 and isinstance(rt_args[0], dict) and isinstance(rt_args[1], str)
    # translate_to_english(text)
    trans_args = rec['translate_to_english']['args']
    assert len(trans_args) == 1 and isinstance(trans_args[0], str)


def test_model_health_single_failure_marks_unhealthy(health_mod):
    _install_stub_list(health_mod, fail_names={'privacy'})
    status, unhealthy = health_mod.model_health()
    assert status == 'unhealthy'
    assert 'privacy' in unhealthy and len(unhealthy) >= 1


def test_model_health_multiple_failures_accumulate(health_mod):
    failing = {'privacy', 'toxicity_check', 'translate_to_english'}
    _install_stub_list(health_mod, fail_names=failing)
    status, unhealthy = health_mod.model_health()
    assert status == 'unhealthy'
    for name in failing:
        assert name in unhealthy
    assert len(unhealthy) == len(failing)


def test_model_health_global_state_reset(health_mod):
    # first run with failure
    _install_stub_list(health_mod, fail_names={'privacy'})
    status1, unhealthy1 = health_mod.model_health()
    assert status1 == 'unhealthy' and 'privacy' in unhealthy1
    # reset globals manually (fixture already resets between tests, but simulate manual reuse)
    health_mod.unhealthy_checks = []
    health_mod.status = 'healthy'
    _install_stub_list(health_mod, fail_names=set())
    status2, unhealthy2 = health_mod.model_health()
    assert status2 == 'healthy' and unhealthy2 == []


def test_model_health_gibberish_bound_method_detection(health_mod):
    # Ensure the special-case branch (scan + Gibberish) is hit; we mark only that stub failing
    _install_stub_list(health_mod, fail_names={'scan'})
    status, unhealthy = health_mod.model_health()
    assert status == 'unhealthy'
    # Gibberish bound method should be recorded as failing
    assert 'scan' in unhealthy