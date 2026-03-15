RULE_REGISTRY = {}

def register_rule(cls):
    RULE_REGISTRY[cls.__name__] = cls
    return cls