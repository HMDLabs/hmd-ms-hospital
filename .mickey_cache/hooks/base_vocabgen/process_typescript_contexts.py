from typing import List
from hmd_lib_mickey.phases import GatherContexts
from hmd_lib_mickey.types import MickeyRunConfiguration


def extract_top_level_namespace(namespace: str) -> str:
    return namespace.split(".")[0]


def extract_dependencies(rels: List):
    deps = []

    rels = list(filter(lambda r: r, rels))

    for rel in rels:
        from_ns = extract_top_level_namespace(rel.get("ref_from"))

        if from_ns != rel["namespace"] and from_ns not in deps:
            deps.append(from_ns)

        to_ns = extract_top_level_namespace(rel.get("ref_to"))

        if to_ns != rel["namespace"] and to_ns not in deps:
            deps.append(to_ns)

    return deps


@GatherContexts.post_hook
def process_contexts(cfg: MickeyRunConfiguration):
    contexts = cfg.contexts

    for k, ctx in contexts.items():
        namespaces = []

        schemas = ctx.get("data", {}).get("nouns", []) + ctx.get("data", {}).get(
            "relationships", []
        )

        schemas = list(filter(lambda c: len(c) >= 1, schemas))

        for item in schemas:
            ns = extract_top_level_namespace(item.get("namespace"))

            if ns is not None and ns not in namespaces:
                namespaces.append(ns)

        contexts[k] = {
            "data": {
                ns: {
                    "nouns": [
                        entity
                        for entity in ctx.get("data", {}).get("nouns", [])
                        if entity
                        and extract_top_level_namespace(entity.get("namespace")) == ns
                    ],
                    "relationships": [
                        entity
                        for entity in ctx.get("data", {}).get("relationships", [])
                        if entity
                        and extract_top_level_namespace(entity.get("namespace")) == ns
                    ],
                }
                for ns in namespaces
            },
            "dependencies": extract_dependencies(
                ctx.get("data", {}).get("relationships", [])
            ),
        }

    return cfg.copy(contexts=contexts)
