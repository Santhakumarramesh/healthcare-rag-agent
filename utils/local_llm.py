"""
utils/local_llm.py
------------------
Privacy-first local LLM using AirLLM + Apple MLX.

Runs Llama 3 8B entirely on-device via layer-by-layer inference.
No data leaves your machine. No API key needed.

Supported models (quantized for speed on M-series):
  - mlx-community/Meta-Llama-3-8B-Instruct-4bit   (~4.7 GB, recommended)
  - mlx-community/Meta-Llama-3.1-8B-Instruct-4bit (~4.7 GB)
  - mlx-community/Mistral-7B-Instruct-v0.3-4bit   (~4.1 GB)

Usage:
    from utils.local_llm import LocalLLM
    llm = LocalLLM()
    response = llm.invoke("What are symptoms of diabetes?")
"""

import os
import platform
from pathlib import Path
from loguru import logger

# Default model — 4-bit quantized, fits in ~5GB RAM, ~20 tok/s on M3
DEFAULT_LOCAL_MODEL = os.getenv(
    "LOCAL_MODEL_ID",
    "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
)

# Cache dir on Mac — models persist across runs
MODEL_CACHE_DIR = Path.home() / ".cache" / "airllm_models"


def is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


class LocalLLM:
    """
    Wraps AirLLM for layer-by-layer local inference on Apple M-series.
    Provides the same .invoke() / .stream() interface as LangChain LLMs
    so it's a drop-in replacement in the pipeline.
    """

    def __init__(self, model_id: str = DEFAULT_LOCAL_MODEL):
        if not is_apple_silicon():
            raise RuntimeError(
                "LocalLLM requires Apple Silicon (M1/M2/M3). "
                "On other hardware, use AirLLM's CUDA path instead."
            )

        self.model_id = model_id
        self._model = None
        logger.info(f"[LocalLLM] Configured: {model_id}")
        logger.info(f"[LocalLLM] Cache dir: {MODEL_CACHE_DIR}")
        logger.info("[LocalLLM] Model will be downloaded on first .invoke() call.")

    def _load(self):
        """Lazy-load the model on first use."""
        if self._model is not None:
            return

        try:
            from airllm import AirLLMLlamaMlx
        except ImportError:
            raise ImportError(
                "AirLLM not installed. Run: pip install airllm mlx mlx-lm"
            )

        logger.info(f"[LocalLLM] Loading model: {self.model_id}")
        logger.info("[LocalLLM] First run downloads the model (~4.7GB). Please wait...")

        MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

        self._model = AirLLMLlamaMlx.from_pretrained(
            self.model_id,
            cache_dir=str(MODEL_CACHE_DIR),
        )
        logger.success("[LocalLLM] Model loaded and ready.")

    def invoke(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.1) -> str:
        """
        Run inference. Returns the full response string.
        Compatible with LangChain .invoke() signature.
        """
        self._load()

        # Llama 3 chat template
        formatted = self._format_prompt(prompt)

        logger.debug(f"[LocalLLM] Generating (max_tokens={max_new_tokens})...")
        tokens = self._model.generate(
            formatted,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            repetition_penalty=1.1,
        )

        # Decode and strip prompt echo
        output = self._model.tokenizer.decode(tokens)
        # Strip the input prompt from output if echoed
        if formatted in output:
            output = output.replace(formatted, "").strip()

        logger.debug(f"[LocalLLM] Generated {len(output)} chars")
        return output

    def stream(self, prompt: str, max_new_tokens: int = 512):
        """
        Token-by-token streaming generator.
        Yields string tokens as they are generated.
        """
        self._load()
        formatted = self._format_prompt(prompt)

        # AirLLM MLX supports streaming via generate with streamer
        from mlx_lm.utils import generate_step
        import mlx.core as mx

        # Tokenize
        input_ids = self._model.tokenizer.encode(formatted, return_tensors="np")
        input_mx = mx.array(input_ids)

        generated = ""
        for token, _ in generate_step(
            input_mx,
            self._model._model,
            max_tokens=max_new_tokens,
            temp=0.1,
        ):
            word = self._model.tokenizer.decode([token])
            generated += word
            yield word

            # Stop at EOS
            if token == self._model.tokenizer.eos_token_id:
                break

    def _format_prompt(self, user_message: str) -> str:
        """Format as Llama 3 instruct chat template."""
        system = (
            "You are a knowledgeable, empathetic Healthcare FAQ Assistant. "
            "Answer accurately using only provided context. "
            "Always recommend consulting a healthcare provider for personal decisions. "
            "Add a medical disclaimer at the end of every response."
        )
        return (
            f"<|begin_of_text|>"
            f"<|start_header_id|>system<|end_header_id|>\n{system}<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n{user_message}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n"
        )

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def get_model_info(self) -> dict:
        cache = MODEL_CACHE_DIR / self.model_id.replace("/", "--")
        return {
            "model_id":    self.model_id,
            "loaded":      self.is_loaded,
            "cache_dir":   str(MODEL_CACHE_DIR),
            "downloaded":  cache.exists(),
            "cache_size":  self._get_cache_size(cache),
            "device":      "Apple MLX (unified memory)",
        }

    def _get_cache_size(self, path: Path) -> str:
        if not path.exists():
            return "not downloaded"
        total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        gb = total / (1024 ** 3)
        return f"{gb:.1f} GB"
