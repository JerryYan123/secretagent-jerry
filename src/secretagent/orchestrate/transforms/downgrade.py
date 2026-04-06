"""Downgrade transform: switch expensive ptools to cheaper implementations."""

from __future__ import annotations

from secretagent.orchestrate.catalog import PtoolCatalog
from secretagent.orchestrate.profiler import PipelineProfile
from secretagent.orchestrate.transforms.base import (
    PipelineTransform, TransformProposal, TransformResult,
)
from secretagent.orchestrate.pipeline import Pipeline

# Ordered from cheapest to most expensive (together_ai pricing)
_CHEAP_MODELS = [
    'together_ai/google/gemma-3n-E4B-it',        # $0.02/$0.04
    'together_ai/openai/gpt-oss-20b',             # $0.05/$0.20
    'together_ai/Qwen/Qwen3.5-9B',               # $0.10/$0.15
    'together_ai/Qwen/Qwen3-Next-80B-A3B-Instruct',  # $0.15/$1.50
]


class DowngradeTransform(PipelineTransform):
    """Switch high-cost ptools to cheaper model implementations.

    Identifies ptools consuming a disproportionate share of cost and
    proposes a config override to use a cheaper LLM model for those
    ptools. This is a config-only change — no pipeline rewriting needed.
    """

    name = 'downgrade'
    requires_llm = False

    def should_apply(self, profile: PipelineProfile) -> bool:
        return any(
            pp.cost_fraction > 0.4
            for pp in profile.ptool_profiles.values()
        )

    def propose(
        self, profile: PipelineProfile, catalog: PtoolCatalog,
    ) -> TransformProposal:
        targets = []
        for name, pp in profile.ptool_profiles.items():
            if pp.cost_fraction > 0.4:
                targets.append({
                    'ptool': name,
                    'cost_fraction': pp.cost_fraction,
                    'avg_cost': pp.avg_cost,
                })

        return TransformProposal(
            transform_name='downgrade',
            rationale=(
                f'Ptool(s) consuming >40% of pipeline cost: '
                f'{", ".join(t["ptool"] for t in targets)}. '
                f'Proposing cheaper model to reduce cost.'
            ),
            changes=targets,
        )

    def apply(
        self,
        proposal: TransformProposal,
        pipeline: Pipeline,
        catalog: PtoolCatalog,
    ) -> TransformResult:
        from secretagent import config

        current_model = config.get('llm.model', '')
        # Pick the cheapest model that isn't the current one
        cheaper = None
        for m in _CHEAP_MODELS:
            if m != current_model:
                cheaper = m
                break
        if cheaper is None:
            return TransformResult(
                success=False,
                message='No cheaper model available to downgrade to.',
            )

        new_config: dict = {}
        downgraded = []
        for change in proposal.changes:
            ptool_name = change['ptool']
            # Config key: ptools.<name>.model overrides llm.model for that ptool
            new_config[f'ptools.{ptool_name}.model'] = cheaper
            downgraded.append(ptool_name)

        return TransformResult(
            success=True,
            new_config=new_config,
            message=(
                f'Downgraded {", ".join(downgraded)} from '
                f'{current_model} to {cheaper}.'
            ),
        )
