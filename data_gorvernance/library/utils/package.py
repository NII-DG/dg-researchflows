import os
import shutil
from collections import OrderedDict

import git
from cookiecutter.main import cookiecutter
from cookiecutter.generate import generate_context
from cookiecutter.config import get_user_config
from cookiecutter.repository import determine_repo_dir
from cookiecutter.prompt import render_variable
from cookiecutter.environment import StrictEnvironment

class MakePackage:

    def __init__(self) -> None:
        self.template_context = OrderedDict([])
        self.rendered_context = OrderedDict([])
        self.prompts = {}

    def get_template(self, template, checkout=None):
        config_dict = get_user_config()
        self.template_dir, cleanup = determine_repo_dir(
            template=template,
            abbreviations=config_dict['abbreviations'],
            clone_to_dir=config_dict['cookiecutters_dir'],
            checkout=checkout,
            no_input=True,
        )
        context_file = os.path.join(self.template_dir,'cookiecutter.json')
        context = generate_context(context_file=context_file)
        self.template_context = context['cookiecutter']
        return self.get_default_context(context)

    def get_default_context(self, context):
        cookiecutter_dict = OrderedDict([])
        env = StrictEnvironment(context=context)

        if '__prompts__' in context['cookiecutter'].keys():
            self.prompts = context['cookiecutter']['__prompts__']
            del context['cookiecutter']['__prompts__']

        all_prompts = context['cookiecutter'].items()
        for key, raw in all_prompts:
            if key.startswith('_'):
                continue
            cookiecutter_dict[key] = render_variable(env, raw, cookiecutter_dict)
        self.rendered_context = cookiecutter_dict
        return cookiecutter_dict

    def get_title(self, var_name):
        prompts = self.prompts
        return (
            prompts[var_name]
            if prompts and var_name in prompts.keys() and prompts[var_name]
            else var_name
        )

    def create_package(self, context_dict=None, output_dir='.'):
        cookiecutter(self.template_dir, no_input=True, extra_context=context_dict, output_dir=output_dir)







