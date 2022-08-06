# Written by Mken from Discord

import bpy
import json

try:
    from join_body_parts_to_body import join_body_parts_to_body
    from genshin_setup_geometry_nodes import setup_geometry_nodes
    from fix_mouth_outlines import fix_face_mouth_outlines_protruding_out
except:
    print('Exception when trying to import required dependency scripts!')

FESTIVITY_ROOT_FOLDER_FILE_PATH = 'festivity_root_folder_file_path'
CHARACTER_MODEL_FOLDER_FILE_PATH = 'character_model_folder_file_path'
COMPONENT_NAME = 'component_name'
BL_IDNAME_FUNCTION = 'function_to_call'
ENABLED = 'enabled'
CACHE_KEY = 'cache_key'

module_path_to_streamlined_setup = ''


def invoke_next_step(current_step_idx: int, file_path_to_cache=None, path_to_streamlined_setup=''):
    if path_to_streamlined_setup:
        global module_path_to_streamlined_setup
        module_path_to_streamlined_setup = path_to_streamlined_setup

    # We use a config.json so that we can make changes without having to restart Blender
    # TODO: Make this a class that gets instantiated in each component? 
    # TOOD: Making a class may allow us to move config.json data back into this module?
    file = open(f'{module_path_to_streamlined_setup}/config.json')
    config = json.load(file)

    cache_file_path = f'{module_path_to_streamlined_setup}/cache.json.tmp'
    if current_step_idx == 1:
        with open(cache_file_path, 'w') as f:
            json.dump({}, f)
    cache_file = open(cache_file_path)
    cache = json.load(cache_file)


    if current_step_idx <= 0 or current_step_idx > len(config):
        return

    previous_step = config.get(str(current_step_idx - 1))
    if file_path_to_cache and previous_step and previous_step[CACHE_KEY]:
        cache_previous_step_file_path(cache, previous_step, file_path_to_cache)
        with open(cache_file_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)
    
    if config[str(current_step_idx)][ENABLED]:
        cached_file_directory = cache.get(config[str(current_step_idx)][CACHE_KEY], '')
        execute_or_invoke = 'EXEC' if cached_file_directory else 'INVOKE'
        component_name = config[str(current_step_idx)][COMPONENT_NAME]
        function_to_use = ComponentFunctionFactory.create_component_function(component_name)

        if type(function_to_use) is bpy.ops._BPyOpsSubModOp:
            print(f'Calling {function_to_use} with {execute_or_invoke}_DEFAULT w/ cache: {cached_file_directory}')
            function_to_use(
                    f'{execute_or_invoke}_DEFAULT', 
                    next_step_idx=current_step_idx + 1, 
                    file_directory=cached_file_directory
            )
        else:
            function_to_use(current_step_idx + 1)
    else:
        invoke_next_step(current_step_idx + 1)


def cache_previous_step_file_path(cache, last_step, file_path_to_cache):
    step_cache_key = last_step.get(CACHE_KEY)

    print(f'Assigning `{step_cache_key}:{file_path_to_cache}` in cache')
    cache[step_cache_key] = file_path_to_cache


class ComponentFunctionFactory:
    @staticmethod
    def create_component_function(component_name):
        if component_name == 'import_materials':
            return bpy.ops.file.genshin_import_materials
        elif component_name == 'join_body_parts_to_body':
            return join_body_parts_to_body
        elif component_name == 'import_character_model':
            return bpy.ops.file.genshin_import_model
        elif component_name == 'import_character_textures':
            return bpy.ops.file.genshin_import_textures
        elif component_name == 'import_outlines':
            return bpy.ops.file.genshin_import_outlines
        elif component_name == 'setup_geometry_nodes':
            return setup_geometry_nodes
        elif component_name == 'import_outline_lightmaps':
            return bpy.ops.file.genshin_import_outline_lightmaps
        elif component_name == 'import_material_data':
            return bpy.ops.file.genshin_import_material_data
        elif component_name == 'fix_mouth_outlines':
            return fix_face_mouth_outlines_protruding_out
        else:
            raise Exception(f'Unknown component name passed into {__name__}: {component_name}')