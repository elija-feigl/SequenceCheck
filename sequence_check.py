#!/usr/bin/env python
""" This script analyses ???
"""

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
__version__ = "0.1"

REVERSE = {
    "A": "T",
    "T": "A",
    "G": "C",
    "C": "G",
}


@dataclass
class Project:
    """Class containing design file and scaffold"""

    design_file: Path
    sequence_file: Path

    design: DnaStructure = field(init=False)

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)
        logging.getLogger("nanodesign").setLevel(logging.ERROR)
        self.design = self._read_design()

    def _read_design(self) -> DnaStructure:
        """read cadnano json file using scaffold sequence file
        using nanodesign package
        """
        converter = Converter()
        converter.modify = True
        if self.design_file.exists():
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
        scaffold = [s.tour for s in self.design.strands if s.is_scaffold][0]
        sequence = "".join([base.seq for base in scaffold.tour])
        return sequence

    def get_staples(self) -> List[str]:
        staples = [s.tour for s in self.design.strands if not s.is_scaffold]
        sequences = []
        for strand in staples:
            sequences.append("".join([base.seq for base in strand.tour]))
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
    logger.info("Score 7mer Scaffold-Staple %s", score["7_scaffold"])
    logger.info("Score 7mer Staple-Scaffold %s", score["7_staple"])
    logger.info("Score 7mer Scaffold-Staple and Staple-Scaffold %s", score["7_both"])


def get_description() -> str:
    return """evaluate scaffold check
              """


def proc_input() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=get_description(),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--design",
        help="cadnano design file",
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
    # command line argmunet parsing
    logger = logging.getLogger(__name__)
    args = proc_input()
    logger.debug("Parsed command line input %s", args)

    # TODO-EF: permutate sequence space. check score for each permutation

    # structure generation
    project = Project(design_file=args.design, sequence_file=args.sequence)
    scaffold = project.get_scaffold()
    staples = project.get_staples()

    score = score_check(scaffold=scaffold, staples=staples)
    print_results(logger=logger, score=score)


if __name__ == "__main__":
    main()
