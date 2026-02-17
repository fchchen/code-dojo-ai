import pytest
from pydantic import ValidationError

from app.schemas import SubmissionRequest


def test_submission_request_rejects_blank_code():
    with pytest.raises(ValidationError):
        SubmissionRequest(code="   ")


def test_submission_request_defaults_username():
    req = SubmissionRequest(code="print('ok')")
    assert req.username == "demo"
