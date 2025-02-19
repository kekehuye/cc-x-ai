from typing import List, Optional, Any

from langchain.callbacks.manager import Callbacks
from langchain.schema import LLMResult

from core.model_providers.error import LLMBadRequestError
from core.model_providers.models.llm.base import BaseLLM
from core.model_providers.models.entity.message import PromptMessage
from core.model_providers.models.entity.model_params import ModelMode, ModelKwargs
from core.third_party.langchain.llms.openllm import OpenLLM


class OpenLLMModel(BaseLLM):
    model_mode: ModelMode = ModelMode.COMPLETION

    def _init_client(self) -> Any:
        self.provider_model_kwargs = self._to_model_kwargs_input(self.model_rules, self.model_kwargs)

        client = OpenLLM(
            server_url=self.credentials.get('server_url'),
            callbacks=self.callbacks,
            llm_kwargs=self.provider_model_kwargs
        )

        return client

    def _run(self, messages: List[PromptMessage],
             stop: Optional[List[str]] = None,
             callbacks: Callbacks = None,
             **kwargs) -> LLMResult:
        """
        run predict by prompt messages and stop words.

        :param messages:
        :param stop:
        :param callbacks:
        :return:
        """
        prompts = self._get_prompt_from_messages(messages)
        return self._client.generate([prompts], stop, callbacks)

    def get_num_tokens(self, messages: List[PromptMessage]) -> int:
        """
        get num tokens of prompt messages.

        :param messages:
        :return:
        """
        prompts = self._get_prompt_from_messages(messages)
        return max(self._client.get_num_tokens(prompts), 0)

    def prompt_file_name(self, mode: str) -> str:
        if 'baichuan' in self.name.lower():
            if mode == 'completion':
                return 'baichuan_completion'
            else:
                return 'baichuan_chat'
        else:
            return super().prompt_file_name(mode)

    def _set_model_kwargs(self, model_kwargs: ModelKwargs):
        pass

    def handle_exceptions(self, ex: Exception) -> Exception:
        return LLMBadRequestError(f"OpenLLM: {str(ex)}")

    @classmethod
    def support_streaming(cls):
        return False
