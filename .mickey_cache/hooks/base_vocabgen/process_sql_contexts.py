from hmd_lib_mickey.phases import GatherContexts
from hmd_lib_mickey.types import MickeyRunConfiguration


@GatherContexts.post_hook
def process_contexts(cfg: MickeyRunConfiguration):
    contexts = {}
    for k, ctx in cfg.contexts.items():
        contexts[k] = {"data": ctx}

    return cfg.copy(contexts=contexts)
