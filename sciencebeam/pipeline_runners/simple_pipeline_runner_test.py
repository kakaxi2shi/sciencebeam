import logging
from mock import patch, MagicMock

import pytest

from sciencebeam.utils.config import dict_to_config
from sciencebeam.utils.mime_type_constants import MimeTypes

from sciencebeam.pipelines import FunctionPipelineStep

from . import simple_pipeline_runner as simple_pipeline_runner_module
from .simple_pipeline_runner import create_simple_pipeline_runner_from_config

DEFAULT_PIPELINE_MODULE = 'sciencebeam.pipelines.default_pipeline'

DEFAULT_CONFIG = {
  u'pipelines': {
    u'default': DEFAULT_PIPELINE_MODULE
  }
}

PDF_FILENAME = 'test.pdf'
PDF_CONTENT = b'pdf content'

@pytest.fixture(name='get_pipeline_for_configuration_and_args', autouse=True)
def _get_pipeline_for_configuration_and_args():
  with patch.object(simple_pipeline_runner_module, 'get_pipeline_for_configuration_and_args') as \
  get_pipeline_for_configuration:

    yield get_pipeline_for_configuration

@pytest.fixture(name='pipeline')
def _pipeline(get_pipeline_for_configuration_and_args):
  return get_pipeline_for_configuration_and_args.return_value

@pytest.fixture(name='args')
def _args():
  return MagicMock(name='args')

@pytest.fixture(name='step')
def _step():
  return MagicMock(name='step')

class TestCreateSimlePipelineFromConfig(object):
  def test_should_call_get_pipeline_for_configuration_with_config_and_args(
    self, get_pipeline_for_configuration_and_args, args):

    config = dict_to_config(DEFAULT_CONFIG)
    create_simple_pipeline_runner_from_config(config, args)
    get_pipeline_for_configuration_and_args.assert_called_with(config, args=args)

  def test_should_pass_args_and_config_to_get_steps(self, pipeline, args, step):
    config = dict_to_config(DEFAULT_CONFIG)
    pipeline.get_steps.return_value = [step]
    create_simple_pipeline_runner_from_config(config, args)
    pipeline.get_steps.assert_called_with(config, args)

  def test_should_load_steps_and_run_them_on_convert(self, pipeline, args, step):
    config = dict_to_config(DEFAULT_CONFIG)
    pipeline.get_steps.return_value = [step]
    pipeline_runner = create_simple_pipeline_runner_from_config(config, args)
    step.get_supported_types.return_value = {MimeTypes.PDF}
    assert (
      pipeline_runner.convert(
        content=PDF_CONTENT, filename=PDF_FILENAME, data_type=MimeTypes.PDF
      ) ==
      step.return_value
    )

  def test_should_skip_first_step_if_content_type_does_not_match(self, pipeline, args, step):
    config = dict_to_config(DEFAULT_CONFIG)
    pipeline.get_steps.return_value = [
      FunctionPipelineStep(lambda _: None, set(), 'dummy'),
      step
    ]
    pipeline_runner = create_simple_pipeline_runner_from_config(config, args)
    step.get_supported_types.return_value = {MimeTypes.PDF}
    assert (
      pipeline_runner.convert(
        content=PDF_CONTENT, filename=PDF_FILENAME, data_type=MimeTypes.PDF
      ) ==
      step.return_value
    )
