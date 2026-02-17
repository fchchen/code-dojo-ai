from unittest.mock import MagicMock, patch

from app.models.registry import ModelRegistry, ModelStatus


class TestModelRegistry:
    def setup_method(self):
        self.registry = ModelRegistry()

    def test_register_model(self):
        self.registry.register("test-model", "org/model-name", "summarization")
        entry = self.registry.get("test-model")
        assert entry.name == "test-model"
        assert entry.model_id == "org/model-name"
        assert entry.status == ModelStatus.NOT_LOADED

    def test_get_unknown_model_raises(self):
        import pytest
        with pytest.raises(KeyError, match="not registered"):
            self.registry.get("nonexistent")

    def test_is_ready_false_when_not_loaded(self):
        self.registry.register("test", "org/m", "task")
        assert not self.registry.is_ready("test")

    @patch("app.models.registry.T5ForConditionalGeneration")
    @patch("app.models.registry.AutoTokenizer")
    def test_load_model_success(self, mock_tokenizer_cls, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        self.registry.register("codet5-test", "Salesforce/codet5-small", "summarization")
        self.registry.load("codet5-test")

        entry = self.registry.get("codet5-test")
        assert entry.status == ModelStatus.READY
        assert entry.model is mock_model
        mock_model.eval.assert_called_once()

    @patch("app.models.registry.AutoModel")
    @patch("app.models.registry.AutoTokenizer")
    def test_load_non_t5_model(self, mock_tokenizer_cls, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        self.registry.register("bert-test", "huggingface/CodeBERTa-small-v1", "embedding")
        self.registry.load("bert-test")

        entry = self.registry.get("bert-test")
        assert entry.status == ModelStatus.READY
        mock_model_cls.from_pretrained.assert_called_once_with("huggingface/CodeBERTa-small-v1")

    @patch("app.models.registry.AutoModelForSeq2SeqLM")
    @patch("app.models.registry.AutoTokenizer")
    def test_load_code_review_model_uses_seq2seq(self, mock_tokenizer_cls, mock_model_cls):
        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        mock_tokenizer_cls.from_pretrained.return_value = MagicMock()

        self.registry.register("review-test", "microsoft/codereviewer", "code-review")
        self.registry.load("review-test")

        entry = self.registry.get("review-test")
        assert entry.status == ModelStatus.READY
        assert entry.model is mock_model
        mock_model_cls.from_pretrained.assert_called_once_with("microsoft/codereviewer")

    @patch("app.models.registry.T5ForConditionalGeneration")
    @patch("app.models.registry.AutoTokenizer")
    def test_load_model_failure_sets_error(self, mock_tokenizer_cls, mock_model_cls):
        mock_model_cls.from_pretrained.side_effect = RuntimeError("OOM")

        self.registry.register("fail-model", "org/codet5-bad", "task")
        self.registry.load("fail-model")

        entry = self.registry.get("fail-model")
        assert entry.status == ModelStatus.ERROR
        assert "OOM" in entry.error

    def test_load_unregistered_raises(self):
        import pytest
        with pytest.raises(KeyError, match="not registered"):
            self.registry.load("ghost")

    def test_status_returns_all_models(self):
        self.registry.register("a", "org/a", "task")
        self.registry.register("b", "org/b", "task")
        status = self.registry.status()
        assert "a" in status
        assert "b" in status
        assert status["a"]["status"] == "not_loaded"

    def test_all_ready_false_when_not_loaded(self):
        self.registry.register("m", "org/m", "t")
        assert not self.registry.all_ready

    @patch("app.models.registry.AutoModel")
    @patch("app.models.registry.AutoTokenizer")
    def test_all_ready_true_when_all_loaded(self, mock_tok, mock_model):
        mock_model.from_pretrained.return_value = MagicMock()
        mock_tok.from_pretrained.return_value = MagicMock()

        self.registry.register("bert-only", "huggingface/CodeBERTa-small-v1", "embed")
        self.registry.load_all()
        assert self.registry.all_ready
