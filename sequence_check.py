#!/usr/bin/env python
""" This script analyses ???
"""
import sys
import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from nanodesign.converters.converter import Converter
from nanodesign.data.dna_structure import DnaStructure

__author__ = "Elija Feigl, Anna Liedl"
__copyright__ = "Copyright 2021, Dietzlab (TUM)"
__credits__ = ["TU München"]
__license__ = "None"
__version__ = "0.2"

REVERSE = {
    "a": "t",
    "t": "a",
    "g": "c",
    "c": "g",
}


@dataclass
class Design:
    """Class containing design file and scaffold"""

    design_file: Path
    sequence_file: Path

    design: DnaStructure = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
        logging.getLogger("nanodesign").setLevel(logging.ERROR)
        self.design = self._read_design()
        self.logger.debug("initialising design sucessfull! YEAH")

    def _read_design(self) -> DnaStructure:
        """read cadnano json file using scaffold sequence file
        using nanodesign package
        """
        converter = Converter()
        converter.modify = True
        if self.design_file.exists() and self.sequence_file.exists():
            converter.read_cadnano_file(
                file_name=str(self.design_file),
                seq_file_name=str(self.sequence_file),
                seq_name=None,
            )
        else:
            self.logger.error(
                "Failed to initialize nanodesign due to missing files: %s %s",
                self.design_file,
                self.sequence_file,
            )
            raise FileNotFoundError
        converter.dna_structure.compute_aux_data()
        return converter.dna_structure

    def get_scaffold(self) -> str:
        scaffolds = [s for s in self.design.strands if s.is_scaffold]
        if len(scaffolds) > 1:
            self.logger.error("too many scaffolds.")
            sys.exit(0)
        else:
            scaffold = scaffolds[0]
        sequence = "".join([base.seq for base in scaffold.tour])
        return sequence.lower()

    def get_staples(self) -> List[str]:
        staples = [s for s in self.design.strands if not s.is_scaffold]
        sequences = list()
        for strand in staples:
            sequence = "".join([base.seq for base in strand.tour])
            sequence = sequence.replace("N", "T")
            sequences.append(sequence.lower())
        return sequences


def score_check(scaffold: str, staples: List[str]) -> Dict[str, int]:
    """YOUR CODE GOES HERE
    input:
        * scaffold string 5'->3'
        * list of staple strings 5'->3'
    output:
        * score dictionary
    """
    score = {"7_scaffold": 0, "7_staple": 0, "7_both": 0}
    return score


def print_results(logger: logging.Logger, score: Dict[str, int]) -> None:
    for key, value in score.items():
        logger.info("Score %s: %s", key, value)


def get_description() -> str:
    return """evaluate scaffold check
              """


def proc_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=get_description(),
    )
    parser.add_argument(
        "-d",
        "--design",
        help="cadnano design file",
        required=True,
        type=str,
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-s",
        "--sequence",
        help="scaffold sequence file, expects .txt",
        required=True,
        type=str,
        default=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | [%(name)s] %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    args = proc_input()
    logger.debug("Parsed command line input %s", args)

    # TODO-EF: permutate sequence space. check score for each permutation

    project = Design(design_file=Path(args.design), sequence_file=Path(args.sequence))
    scaffold = project.get_scaffold()
    staples = project.get_staples()

    score = score_check(scaffold=scaffold, staples=staples)
    print_results(logger=logger, score=score)


if __name__ == "__main__":
    main()
