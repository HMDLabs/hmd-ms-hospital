from hmd_lib_mickey.phases import GatherContexts
from hmd_lib_mickey.types import MickeyRunConfiguration


@GatherContexts.post_hook
def process_contexts(cfg: MickeyRunConfiguration):
    contexts = {}
    for k, ctx in cfg.contexts.items():
        contexts[k] = {"data": ctx["data"], "from": ctx["from"], "to": ctx["to"]}

    return cfg.copy(contexts=contexts)
