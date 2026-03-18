RULE_REGISTRY = {}

def register_rule(cls):
    RULE_REGISTRY[cls.__name__] = cls
    print(RULE_REGISTRY)
    return cls