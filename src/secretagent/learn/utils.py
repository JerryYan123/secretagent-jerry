"""Utilities for collecting training data from recorded interface calls."""

import json
import os
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from secretagent import config, savefile
from secretagent.dataset import Case, Dataset

def collect_interface_data(
        dirs: list[Path], interface_name: str, file_under: str) -> tuple[Path, Dataset]:
    """Collect input/output pairs for an interface from recording directories.

    Creates a timestamped directory under config.get('train_dir') containing:
        data.json       — a JSON-serialized Dataset of input/output pairs
        sources.txt     — one source directory name per line
        source_configs/ — a copy of each source directory's config.yaml

    Args:
        dirs: recording directories (already filtered via savefile.filter_paths)
        interface_name: interface name to extract from rollouts
        file_under: tag for the output directory name

    Returns:
        Path to the created output directory.
    """
    # create destination files
    train_dir = config.require('train_dir') 
    dataset_filename, sources_filename, source_cfg_dirname = savefile.filename_list(  
        train_dir, ['data.json', 'sources.txt', 'source_configs'], file_under)

    # create and save dataset
    cases = _extract_cases_from_dirs(dirs, interface_name)
    dataset = Dataset(name=interface_name, cases=cases)
    with open(dataset_filename, 'w') as f:
        f.write(dataset.model_dump_json(indent=2))
    
    # Save source directory names
    with open(sources_filename, 'w') as f:
        for d in dirs:
            f.write(f'{d}\n')

    # Copy source configs
    os.makedirs(source_cfg_dirname, exist_ok=True)
    for d in dirs:
        src_cfg = Path(d) / 'config.yaml'
        if not src_cfg.exists():
            raise ValueError(f'missing config file {src_cfg}')
        shutil.copy2(src_cfg, source_cfg_dirname / f'{d.name}.yaml')

    return dataset_filename.parent, dataset

def _extract_cases_from_record(
        dx: int, lx: int, interface_name: str, record: dict[str, Any]) -> Iterator[Case]:
    """Yield Cases for the named interface from a single JSONL record."""
    for sx, step in enumerate(record.get('rollout', [])):
        if step['func'] == interface_name:
            case = Case(
                name=f'{interface_name}_{dx}.{lx}.{sx}',
                input_args=step.get('args'),
                input_kw=step.get('kw') or None,
                expected_output=step.get('output')
            )
            yield case
                

def _extract_cases_from_dirs(dirs: list[Path], interface_name: str) -> list[Case]:
    """Extract Cases for the named interface from results.jsonl in each directory."""
    result = []
    for dx, d in enumerate(dirs):
        jsonl_path = Path(d) / 'results.jsonl'
        if not jsonl_path.exists():
            raise ValueError(f'missing jsonl file {jsonl_path}')
        with open(jsonl_path) as f:
            for lx, line in enumerate(f):
                record = json.loads(line)
                for case in _extract_cases_from_record(dx, lx, interface_name, record):
                    result.append(case)
    return result
