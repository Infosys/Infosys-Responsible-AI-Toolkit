import pytest


try:
    # Try to import to check if CLIP models are available
    from image_explain.utils.metrics.alignment_score import AlignmentScore
    from image_explain.utils.metrics.aesthetic_score import AestheticScore
    METRICS_AVAILABLE = True
except (ImportError, ValueError) as e:
    METRICS_AVAILABLE = False
    SKIP_REASON = f"Metrics modules unavailable: {str(e)}"


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="CLIP models not available during test import")
class TestMetricsSkipped:
    """Placeholder for metrics tests when CLIP models are unavailable"""
    
    def test_metrics_import_status(self):
        """Document metrics availability status"""
        if not METRICS_AVAILABLE:
            pytest.skip("Metrics modules could not be imported due to CLIP model loading")
