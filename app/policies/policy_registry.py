POLICY_REGISTRY: dict[str, type] = {}

def register_policy(cls):
    POLICY_REGISTRY[cls.__name__] = cls
    return cls
 