import glob
import importlib.util
import os
import pydantic
import inspect

def collect_schema(folder_path):
    """
    Collects all the pydantic models from the files in the given folder path and returns a formatted string.
    """
    schema = ""

    files = glob.glob(f"{folder_path}/**/*.py", recursive=True) # Get all the Python files in the folder path

    for file in files:
        try:
            module_name = os.path.splitext(os.path.basename(file))[0] # Get the module name from the file path

            spec = importlib.util.spec_from_file_location(module_name, file) # Import the module dynamically
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module): # Iterate through the attributes of the module
                if inspect.isclass(obj) and issubclass(obj, pydantic.BaseModel) and obj is not pydantic.BaseModel: # Check if the object is a subclass of Pydantic's BaseModel and not BaseModel itself
                    # Get the schema of the Pydantic model (for Pydantic v2)
                    schema += f"Model: {name}\n"
                    schema += f"{obj.model_json_schema()}\n\n"
        except Exception as e:
            print(f"Error processing {file}: {e}") # If any error occurs, log the file and continue with other files

    return schema