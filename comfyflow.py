from comfyclient import ComfyClient
import copy
import json
from loguru import logger
from PIL import Image
import random

##
## Credits to https://github.com/xingren23/ComfyFlowApp
## slight modification to introduce prompt
##

class ComfyFlow:
    def __init__(self, comfy_client, api_data) -> any:
    
        self.comfy_client = comfy_client
        self.api_json = json.loads(api_data)

    def generate_json(self, user_prompt):
        prompt = copy.deepcopy(self.api_json)
        if prompt is not None:
            # update seed and noise_seed for random, if not set
            for node_id in prompt:
                node = prompt[node_id]
                node_inputs = node['inputs']
                for param_name in node_inputs:
                    param_value = node_inputs[param_name]
                    if isinstance(param_value, int):
                        if (param_name == "seed" or param_name == "noise_seed"):
                            random_value = random.randint(0, 0x7fffffffffffffff)
                            prompt[node_id]['inputs'][param_name] = random_value
                            logger.info(f"update prompt with random, {node_id} {param_name} {param_value} to {random_value}")
                    if (param_name == "text"):
                            prompt[node_id]['inputs'][param_name] = user_prompt
                            logger.info(f"update prompt with prompt text, {node_id} {param_name} {param_value} to {user_prompt}")
        return prompt
