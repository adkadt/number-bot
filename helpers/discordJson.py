import json
import os


class DiscordJson():

    def open(fileName):
        serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
        with open(serverInfoFileName, 'r') as serverInfoFile:
            jsonData = json.load(serverInfoFile)
        return jsonData


    def write(fileName, jsonData):
        serverInfoFileName = f"{os.path.realpath(os.path.dirname(__file__))}/../data/{fileName}.json"
        with open(serverInfoFileName, 'w') as serverInfoFile:
            json.dump(jsonData, serverInfoFile, sort_keys=False, indent=4)


    @classmethod
    def sort_json_numerically(cls, obj):
        """
        Recursively sort JSON keys numerically where possible.
        Non-numeric keys are sorted alphabetically after numeric keys.
        """
        if isinstance(obj, dict):
            # Sort dictionary keys
            def sort_key(k):
                # Try to convert to number for sorting
                try:
                    return (0, float(k))  # Numeric keys come first
                except (ValueError, TypeError):
                    return (1, k)  # Non-numeric keys come second
            
            sorted_dict = {k: cls.sort_json_numerically(obj[k]) 
                        for k in sorted(obj.keys(), key=sort_key)}
            return sorted_dict
        
        elif isinstance(obj, list):
            # Recursively sort any dictionaries in lists
            return [cls.sort_json_numerically(item) for item in obj]
        
        else:
            # Return primitive values as-is
            return obj