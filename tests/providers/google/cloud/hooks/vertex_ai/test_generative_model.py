#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from unittest import mock

import pytest

from airflow.exceptions import (
    AirflowProviderDeprecationWarning,
)

# For no Pydantic environment, we need to skip the tests
pytest.importorskip("google.cloud.aiplatform_v1")
vertexai = pytest.importorskip("vertexai.generative_models")
from vertexai.generative_models import HarmBlockThreshold, HarmCategory, Tool, grounding

from airflow.providers.google.cloud.hooks.vertex_ai.generative_model import (
    GenerativeModelHook,
)
from tests.providers.google.cloud.utils.base_gcp_mock import (
    mock_base_gcp_hook_default_project_id,
)

TEST_GCP_CONN_ID: str = "test-gcp-conn-id"
GCP_PROJECT = "test-project"
GCP_LOCATION = "us-central1"

TEST_PROMPT = "In 10 words or less, what is apache airflow?"
TEST_CONTENTS = [TEST_PROMPT]
TEST_LANGUAGE_PRETRAINED_MODEL = "text-bison"
TEST_TEMPERATURE = 0.0
TEST_MAX_OUTPUT_TOKENS = 256
TEST_TOP_P = 0.8
TEST_TOP_K = 40

TEST_TEXT_EMBEDDING_MODEL = ""

TEST_MULTIMODAL_PRETRAINED_MODEL = "gemini-pro"
TEST_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}
TEST_GENERATION_CONFIG = {
    "max_output_tokens": TEST_MAX_OUTPUT_TOKENS,
    "top_p": TEST_TOP_P,
    "temperature": TEST_TEMPERATURE,
}
TEST_TOOLS = [Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())]

TEST_MULTIMODAL_VISION_MODEL = "gemini-pro-vision"
TEST_VISION_PROMPT = "In 10 words or less, describe this content."
TEST_MEDIA_GCS_PATH = "gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg"
TEST_MIME_TYPE = "image/jpeg"

SOURCE_MODEL = "gemini-1.0-pro-002"
TRAIN_DATASET = "gs://cloud-samples-data/ai-platform/generative_ai/sft_train_data.jsonl"

BASE_STRING = "airflow.providers.google.common.hooks.base_google.{}"
GENERATIVE_MODEL_STRING = "airflow.providers.google.cloud.hooks.vertex_ai.generative_model.{}"


def assert_warning(msg: str, warnings):
    assert any(msg in str(w) for w in warnings)


class TestGenerativeModelWithDefaultProjectIdHook:
    def dummy_get_credentials(self):
        pass

    def setup_method(self):
        with mock.patch(
            BASE_STRING.format("GoogleBaseHook.__init__"), new=mock_base_gcp_hook_default_project_id
        ):
            self.hook = GenerativeModelHook(gcp_conn_id=TEST_GCP_CONN_ID)
            self.hook.get_credentials = self.dummy_get_credentials

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_text_generation_model"))
    def test_prompt_language_model(self, mock_model) -> None:
        with pytest.warns(AirflowProviderDeprecationWarning) as warnings:
            self.hook.prompt_language_model(
                project_id=GCP_PROJECT,
                location=GCP_LOCATION,
                prompt=TEST_PROMPT,
                pretrained_model=TEST_LANGUAGE_PRETRAINED_MODEL,
                temperature=TEST_TEMPERATURE,
                max_output_tokens=TEST_MAX_OUTPUT_TOKENS,
                top_p=TEST_TOP_P,
                top_k=TEST_TOP_K,
            )
            assert_warning("text_generation_model_predict", warnings)

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_text_embedding_model"))
    def test_generate_text_embeddings(self, mock_model) -> None:
        with pytest.warns(AirflowProviderDeprecationWarning) as warnings:
            self.hook.generate_text_embeddings(
                project_id=GCP_PROJECT,
                location=GCP_LOCATION,
                prompt=TEST_PROMPT,
                pretrained_model=TEST_TEXT_EMBEDDING_MODEL,
            )
            assert_warning("text_embedding_model_get_embeddings", warnings)

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_generative_model"))
    def test_prompt_multimodal_model(self, mock_model) -> None:
        with pytest.warns(AirflowProviderDeprecationWarning) as warnings:
            self.hook.prompt_multimodal_model(
                project_id=GCP_PROJECT,
                location=GCP_LOCATION,
                prompt=TEST_PROMPT,
                generation_config=TEST_GENERATION_CONFIG,
                safety_settings=TEST_SAFETY_SETTINGS,
                pretrained_model=TEST_MULTIMODAL_PRETRAINED_MODEL,
            )
            assert_warning("generative_model_generate_content", warnings)

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_generative_model_part"))
    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_generative_model"))
    def test_prompt_multimodal_model_with_media(self, mock_model, mock_part) -> None:
        with pytest.warns(AirflowProviderDeprecationWarning) as warnings:
            self.hook.prompt_multimodal_model_with_media(
                project_id=GCP_PROJECT,
                location=GCP_LOCATION,
                prompt=TEST_VISION_PROMPT,
                generation_config=TEST_GENERATION_CONFIG,
                safety_settings=TEST_SAFETY_SETTINGS,
                pretrained_model=TEST_MULTIMODAL_VISION_MODEL,
                media_gcs_path=TEST_MEDIA_GCS_PATH,
                mime_type=TEST_MIME_TYPE,
            )
            assert_warning("generative_model_generate_content", warnings)

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_text_generation_model"))
    def test_text_generation_model_predict(self, mock_model) -> None:
        self.hook.text_generation_model_predict(
            project_id=GCP_PROJECT,
            location=GCP_LOCATION,
            prompt=TEST_PROMPT,
            pretrained_model=TEST_LANGUAGE_PRETRAINED_MODEL,
            temperature=TEST_TEMPERATURE,
            max_output_tokens=TEST_MAX_OUTPUT_TOKENS,
            top_p=TEST_TOP_P,
            top_k=TEST_TOP_K,
        )
        mock_model.assert_called_once_with(TEST_LANGUAGE_PRETRAINED_MODEL)
        mock_model.return_value.predict.assert_called_once_with(
            prompt=TEST_PROMPT,
            temperature=TEST_TEMPERATURE,
            max_output_tokens=TEST_MAX_OUTPUT_TOKENS,
            top_p=TEST_TOP_P,
            top_k=TEST_TOP_K,
        )

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_text_embedding_model"))
    def test_text_embedding_model_get_embeddings(self, mock_model) -> None:
        self.hook.text_embedding_model_get_embeddings(
            project_id=GCP_PROJECT,
            location=GCP_LOCATION,
            prompt=TEST_PROMPT,
            pretrained_model=TEST_TEXT_EMBEDDING_MODEL,
        )
        mock_model.assert_called_once_with(TEST_TEXT_EMBEDDING_MODEL)
        mock_model.return_value.get_embeddings.assert_called_once_with([TEST_PROMPT])

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_generative_model"))
    def test_generative_model_generate_content(self, mock_model) -> None:
        self.hook.generative_model_generate_content(
            project_id=GCP_PROJECT,
            contents=TEST_CONTENTS,
            location=GCP_LOCATION,
            tools=TEST_TOOLS,
            generation_config=TEST_GENERATION_CONFIG,
            safety_settings=TEST_SAFETY_SETTINGS,
            pretrained_model=TEST_MULTIMODAL_PRETRAINED_MODEL,
        )
        mock_model.assert_called_once_with(TEST_MULTIMODAL_PRETRAINED_MODEL)
        mock_model.return_value.generate_content.assert_called_once_with(
            contents=TEST_CONTENTS,
            tools=TEST_TOOLS,
            generation_config=TEST_GENERATION_CONFIG,
            safety_settings=TEST_SAFETY_SETTINGS,
        )

    @mock.patch("vertexai.preview.tuning.sft.train")
    def test_supervised_fine_tuning_train(self, mock_sft_train) -> None:
        self.hook.supervised_fine_tuning_train(
            project_id=GCP_PROJECT,
            location=GCP_LOCATION,
            source_model=SOURCE_MODEL,
            train_dataset=TRAIN_DATASET,
        )

        # Assertions
        mock_sft_train.assert_called_once_with(
            source_model=SOURCE_MODEL,
            train_dataset=TRAIN_DATASET,
            validation_dataset=None,
            epochs=None,
            adapter_size=None,
            learning_rate_multiplier=None,
            tuned_model_display_name=None,
        )

    @mock.patch(GENERATIVE_MODEL_STRING.format("GenerativeModelHook.get_generative_model"))
    def test_count_tokens(self, mock_model) -> None:
        self.hook.count_tokens(
            project_id=GCP_PROJECT,
            contents=TEST_CONTENTS,
            location=GCP_LOCATION,
            pretrained_model=TEST_MULTIMODAL_PRETRAINED_MODEL,
        )
        mock_model.assert_called_once_with(TEST_MULTIMODAL_PRETRAINED_MODEL)
        mock_model.return_value.count_tokens.assert_called_once_with(
            contents=TEST_CONTENTS,
        )
