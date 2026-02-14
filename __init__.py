import os
import sys
import folder_paths

custom_nodes_path = os.path.join(folder_paths.base_path, "custom_nodes")
onebuttonprompt_path = os.path.join(custom_nodes_path, "OneButtonPrompt")
sys.path.append(onebuttonprompt_path)

from .OneButtonPromptNodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# API Route for preset syncing
from server import PromptServer
from aiohttp import web
from .one_button_presets import OBPresets

@PromptServer.instance.routes.get("/one_button_prompt/get_preset")
async def get_preset(request):
    preset_name = request.rel_url.query.get("name", "")
    if not preset_name:
        return web.json_response({})
    
    preset_data = {}
    if preset_name == "Standard":
        # Standard might be a special case or just a default
        preset_data = OBPresets.get_obp_preset("Standard")
    else:
        # Load preset logic
        preset_data = OBPresets.get_obp_preset(preset_name)
    
    return web.json_response(preset_data)

WEB_DIRECTORY = "./js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']