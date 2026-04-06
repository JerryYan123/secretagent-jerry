"""Repair transform: fix ptools that produce frequent errors."""

from __future__ import annotations

from secretagent.orchestrate.catalog import PtoolCatalog
from secretagent.orchestrate.profiler import PipelineProfile
from secretagent.orchestrate.transforms.base import (
    PipelineTransform, TransformProposal, TransformResult,
)
from secretagent.orchestrate.pipeline import Pipeline


class RepairTransform(PipelineTransform):
    """Fix ptools with recurring error patterns.

    Implementation guide:
    Analyze error_patterns from the profiler to identify common failure
    modes. Generate error-handling code or alternative tool call sequences
    to handle those failure cases.
    """

    name = 'repair'
    requires_llm = True

    def should_apply(self, profile: PipelineProfile) -> bool:
        return any(
            pp.error_patterns
            for pp in profile.ptool_profiles.values()
        )

    def propose(
        self, profile: PipelineProfile, catalog: PtoolCatalog,
    ) -> TransformProposal:
        raise NotImplementedError('TODO: implement repair transform')

    def apply(
        self,
        proposal: TransformProposal,
        pipeline: Pipeline,
        catalog: PtoolCatalog,
    ) -> TransformResult:
        raise NotImplementedError('TODO: implement repair transform')
