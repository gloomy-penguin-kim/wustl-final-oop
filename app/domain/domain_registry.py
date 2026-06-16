DOMAIN_REGISTRY: dict[str, type] = {}

def register_domain(cls):
    DOMAIN_REGISTRY[cls.__name__] = cls
    return cls
