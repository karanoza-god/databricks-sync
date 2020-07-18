import json
import os
from ctypes import *
from typing import Text, Any, Dict

so_path = os.path.join(os.path.dirname(__file__), 'json2hcl.so')
lib = cdll.LoadLibrary(so_path)


class GoString(Structure):
    _fields_ = [("p", c_char_p), ("n", c_longlong)]


# Python representation of the C struct for CreateResourceHCLResponse
class CreateHCLResponse(Structure):
    _fields_ = [("hcl", c_char_p), ("error", c_char_p)]


lib.CreateHCLFromJson.argtypes = [GoString, GoString, GoString, GoString, c_ubyte]
lib.CreateHCLFromJson.restype = CreateHCLResponse


def create_hcl_from_json(object_type: Text, object_name: Text, object_identifier: Text,
                         object_data_dictionary: Dict[Text, Any], debug: bool) -> Text:
    b_object_type = object_type.encode("UTF-8")
    b_object_name = object_name.encode("UTF-8")
    b_object_identifier = object_identifier.encode("UTF-8")
    # Load object as dictionary
    json_str = json.dumps(object_data_dictionary)
    b_json_str = json_str.encode("UTF-8")

    go_object_type = GoString(b_object_type, len(b_object_type))
    go_object_name = GoString(b_object_name, len(b_object_name))
    go_object_identifier = GoString(b_object_identifier, len(b_object_identifier))
    go_json_str = GoString(b_json_str, len(b_json_str))

    debug_option = 1 if debug else 0
    output = lib.CreateHCLFromJson(go_object_type, go_object_name, go_object_identifier, go_json_str,
                                   c_ubyte(debug_option))
    if len(output.error) > 0:
        raise ValueError(output.error.decode("UTF-8"))
    else:
        return output.hcl.decode("UTF-8")
