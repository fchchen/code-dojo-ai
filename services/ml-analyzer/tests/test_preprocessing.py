from app.pipelines.preprocessing import detect_language, preprocess, truncate_code


class TestDetectLanguage:
    def test_detects_python(self):
        code = "def hello():\n    import os\n    print('hi')"
        assert detect_language(code) == "python"

    def test_detects_java(self):
        code = "public class Main {\n    private int x;\n    System.out.println(x);\n}"
        assert detect_language(code) == "java"

    def test_detects_javascript(self):
        code = "const x = 5;\nconst fn = () => console.log(x);"
        assert detect_language(code) == "javascript"

    def test_detects_typescript(self):
        code = "interface User {\n  name: string;\n  age: number;\n}"
        assert detect_language(code) == "typescript"

    def test_returns_unknown_for_plain_text(self):
        assert detect_language("hello world nothing here") == "unknown"


class TestTruncateCode:
    def test_short_code_unchanged(self):
        code = "x = 1\ny = 2"
        assert truncate_code(code, max_tokens=100) == code

    def test_long_code_truncated(self):
        code = "\n".join(f"line_{i} = {i}" for i in range(200))
        result = truncate_code(code, max_tokens=10)
        assert len(result) < len(code)

    def test_empty_code(self):
        assert truncate_code("", max_tokens=10) == ""

    def test_single_long_line(self):
        code = "x " * 1000
        result = truncate_code(code, max_tokens=5)
        assert result == code.splitlines()[0]


class TestPreprocess:
    def test_returns_expected_fields(self):
        result = preprocess("def foo(): pass")
        assert "code" in result
        assert "language" in result
        assert "original_length" in result
        assert "truncated" in result

    def test_detects_language(self):
        result = preprocess("def foo(): pass")
        assert result["language"] == "python"

    def test_truncation_flag(self):
        short = preprocess("x = 1")
        assert short["truncated"] is False

        long_code = "\n".join(f"variable_{i} = {i}" for i in range(1000))
        long_result = preprocess(long_code, max_tokens=10)
        assert long_result["truncated"] is True
