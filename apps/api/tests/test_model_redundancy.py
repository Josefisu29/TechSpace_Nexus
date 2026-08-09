import pytest

from model_registry import ModelRecord, ModelStatus, approve, candidates, register, set_status
from model_failover import FailoverRouter, ModelUnavailable
from model_backup import register_artifact, verify_artifact


def setup_function():
    from model_registry import REGISTRY
    from model_backup import ARTIFACTS
    REGISTRY.clear()
    ARTIFACTS.clear()


def test_registry_requires_pinned_revision():
    with pytest.raises(ValueError):
        register(ModelRecord("x", "ollama", "PIN_REQUIRED", "MIT", ("general",), 8192))


def test_failover_uses_approved_healthy_fallback():
    register(ModelRecord("primary", "local", "r1", "MIT", ("general",), 8192, priority=100, fallbacks=("backup",)))
    register(ModelRecord("backup", "local", "r2", "MIT", ("general",), 8192, priority=90))
    approve("primary")
    approve("backup")
    set_status("primary", ModelStatus.degraded)
    router = FailoverRouter(max_attempts=2)
    assert [m.id for m in router.plan("general")] == ["backup"]


def test_artifact_checksum():
    ref = register_artifact("primary", "r1", "s3://bucket/model", b"weights")
    assert verify_artifact(ref, b"weights")
    assert not verify_artifact(ref, b"tampered")
