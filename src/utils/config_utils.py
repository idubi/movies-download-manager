def parse_params(params):
    param_tuples = []
    for param in params.split(" "):
        if "=" in param:
            key, value = param.split("=")
            key = key.strip()
            value = value.strip('"').strip()
            param_tuples.append((key, value)) 
    return param_tuples


def get_param_value(param_tuples, key, default=None):
    return dict(param_tuples).get(key, default)


def validate_params(param_tuples, mandatory_parameters, error_message):
    param_keys = [key for key, _ in param_tuples]
    for mandatory_param in mandatory_parameters:
        if mandatory_param not in param_keys:
            print(f"{error_message} - Missing mandatory parameter: {mandatory_param}")
            return False
    return True


def add_default_value(param_tuples, key, default_value):
    if not any(k == key for k, _ in param_tuples):
        param_tuples.append((key, default_value))
