# llm/interpreter.py
# Async LLM interpreter with background thread and polling

import os
import threading
from typing import Optional, List

from llm.backends import BACKEND_REGISTRY
from llm.prompts import build_system_prompt, build_user_prompt


class LLMInterpreter:
    """Manages LLM API calls for plate interpretation.

    Usage:
        interpreter = LLMInterpreter()
        interpreter.interpret_async(plate_text, personas, purpose, ...)

        # In main loop each frame:
        if interpreter.has_result:
            text = interpreter.get_result()
        elif interpreter.has_error:
            error = interpreter.get_error()
    """

    def __init__(self):
        self._config = {}
        self._load_config()
        self.backend = self._create_backend()

        # Async state (GIL-atomic, no lock needed)
        self._busy = False
        self._result: Optional[str] = None
        self._error: Optional[str] = None

    def _load_config(self):
        """Load configuration from .env file and/or environment variables."""
        config = {}

        # Try .env file in project root
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_path):
            with open(env_path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"').strip("'")

        # Environment variables override .env
        for key in ('LLM_PROVIDER', 'LLM_MODEL',
                    'ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY'):
            env_val = os.environ.get(key)
            if env_val:
                config[key] = env_val

        self._config = config

    def _create_backend(self):
        """Instantiate the correct backend based on LLM_PROVIDER config."""
        provider = self._config.get('LLM_PROVIDER', 'anthropic').lower()
        model_override = self._config.get('LLM_MODEL')

        if provider not in BACKEND_REGISTRY:
            return None  # Will be caught at interpret time

        backend_cls, key_name = BACKEND_REGISTRY[provider]
        api_key = self._config.get(key_name, '')

        backend = backend_cls(api_key=api_key)
        if model_override:
            backend.default_model = model_override

        return backend

    @property
    def is_busy(self) -> bool:
        return self._busy

    @property
    def has_result(self) -> bool:
        return self._result is not None

    @property
    def has_error(self) -> bool:
        return self._error is not None

    def get_result(self) -> Optional[str]:
        """Consume and return the result. Resets after read."""
        result = self._result
        self._result = None
        return result

    def get_error(self) -> Optional[str]:
        """Consume and return the error. Resets after read."""
        error = self._error
        self._error = None
        return error

    def interpret_async(self, plate_text: str, personas: List[str],
                        purpose: str, day_stem: str, day_branch: str):
        """Launch interpretation in a background thread.

        Results are polled via has_result/has_error properties.
        """
        if self._busy:
            return

        self._busy = True
        self._result = None
        self._error = None

        thread = threading.Thread(
            target=self._run_interpretation,
            args=(plate_text, personas, purpose, day_stem, day_branch),
            daemon=True,
        )
        thread.start()

    def _run_interpretation(self, plate_text: str, personas: List[str],
                            purpose: str, day_stem: str, day_branch: str):
        """Background thread: build prompts and call LLM API."""
        try:
            provider = self._config.get('LLM_PROVIDER', 'anthropic').lower()

            if self.backend is None:
                self._error = f"不支持的LLM提供商：{provider}\n支持：{', '.join(BACKEND_REGISTRY.keys())}"
                return

            if not self.backend.api_key:
                _, key_name = BACKEND_REGISTRY[provider]
                self._error = (
                    f"未找到API密钥。\n"
                    f"请在项目根目录的 .env 文件中设置 {key_name}=your-key\n"
                    f"或设置同名环境变量。"
                )
                return

            system_prompt = build_system_prompt(personas)
            user_prompt = build_user_prompt(plate_text, purpose,
                                            day_stem, day_branch)

            self._result = self.backend.call(system_prompt, user_prompt)

        except ImportError as e:
            pkg_name = str(e).split("'")[-2] if "'" in str(e) else provider
            self._error = (
                f"未安装 {pkg_name} 包。\n"
                f"请运行：pip install {pkg_name}"
            )
        except Exception as e:
            self._error = f"API调用失败：{e}"
        finally:
            self._busy = False
