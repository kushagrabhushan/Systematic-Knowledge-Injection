import pandas as pd
import os
import sys
import numpy as np
import json
from collections import defaultdict
from collections import Counter
import argparse
import re
import string
import itertools
import random


def parse_arguments(arg_string=None):
    parser = argparse.ArgumentParser(description=" ")
    parser.add_argument("--input_dir", type=str, help="path to save the datset.")
    parser.add_argument("--output_dir", type=str, help="path to save the datset.")
    parser.add_argument("--corrupt_prob", type=float, default=0)
    parser.add_argument("--single_nodes_file", type=str, default=None)
    parser.add_argument("--text_col_in_single_nodes", type=str, default="document")
    parser.add_argument("--seed", type=int, default=4020)
    parser.add_argument(
        "--corruption_strategy",
        type=str,
        choices=["orig", "reverse", "random"],
        default="orig",
        help="after deleting gold ids, how to order the retrieved ids?",
    )

    parser.add_argument(
        "--retain_existing_corruption_for_train",
        type=int,
        default=1,
        help="input data itself may have retriever failures. Should we keep those intact for train data or erase all initial corruption so that retriever success is mimicked even for them?",
    )

    if arg_string is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_string.split())

    return args


def force_retriever_failure(row, args):
    gold_ids = row["int_id_list"]
    retrieved_ids = row["retrieved_ids"]
    return_ids = []

    for this_id in retrieved_ids:
        if this_id not in gold_ids:
            return_ids.append(this_id)
    #

    if args.corruption_strategy == "random":
        random.shuffle(return_ids)
    elif args.corruption_strategy == "reverse":
        return_ids.reverse()

    return return_ids


def select_retrieved_ids(row, topk, corrupt_prob):
    if (len(row["corrupt_retrieved_ids"]) >= topk) and (
        random.choices([0, 1], weights=[1.0 - corrupt_prob, corrupt_prob])[0] == 1
    ):
        return 1
    else:
        return 0


def reduce_corruption_to_zero(tab, args, myprint):
    myprint("Using gold passages...")
    myprint("create a map from passage id to passage text")
    id2passage = {}

    single_nodes = pd.read_json(args.single_nodes_file, lines=True)

    for _, row in single_nodes.iterrows():
        id2passage[row["int_id"]] = row[args.text_col_in_single_nodes]

    tab["gold_passages"] = tab["int_id_list"].apply(
        lambda x: [id2passage[int_id] for int_id in x]
    )
    tab["start_at"] = tab["int_id_list"].apply(
        lambda x: random.randint(0, max(0, (len(x) - 5)))
    )

    tab["retrieved_ids"] = tab.apply(
        lambda row: row["retrieved_ids"]

        if row["in_top5"] == 1
        else row["int_id_list"][row["start_at"] : (row["start_at"] + 10)]
        + row["retrieved_ids"],
        axis=1,
    )
    tab["retrieved_passages"] = tab.apply(
        lambda row: [id2passage[x] for x in row["retrieved_ids"]], axis=1
    )
    del tab["gold_passages"]
    del tab["start_at"]
    tab["in_top5"] = 1

    return tab


def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)
    input_files = os.listdir(args.input_dir)
    input_files = [
        x for x in input_files if os.path.isfile(os.path.join(args.input_dir, x))
    ]
    log_file = os.path.join(args.input_dir, f"CORRUPTION_LOGS_{args.corrupt_prob}")
    log_handle = open(log_file, "a")

    def myprint(*args, **kwargs):
        print(*args, **kwargs, file=log_handle)
        print(*args, **kwargs)

    myprint("********** START NEW RUN ********")
    input_files = [x for x in input_files if x.endswith((".jsonl", ".json"))]
    myprint(input_files)

    for ind, this_file in enumerate(input_files):
        myprint(os.path.join(args.input_dir, this_file))
        output_file = os.path.join(args.output_dir, this_file)

        if os.path.exists(output_file):
            print("Output file exists... Skipping... ")

            continue
        tab = pd.read_json(
            os.path.join(args.input_dir, this_file), lines=this_file.endswith(".jsonl")
        )

        if "orig_retrieved_ids" in tab.columns:
            myprint("Looks like source data has already been corrupted")
            raise

        original_columns = list(tab.columns)

        tab["in_top5"] = tab.apply(
            lambda row: 1

            if (
                len(set(row["retrieved_ids"][:5]).intersection(set(row["int_id_list"])))
                > 0
            )
            else 0,
            axis=1,
        )

        tab["orig_retrieved_ids"] = tab["retrieved_ids"]
        tab["orig_retrieved_passages"] = tab["retrieved_passages"]

        tab["question"] = tab["question"].apply(lambda x: x.strip())

        myprint(
            "Stats before corruption:"
        )  # , tab.groupby('in_top5')['question'].describe())
        myprint(tab["in_top5"].mean())

        if args.corrupt_prob == 0:
            myprint("Using gold passages...")
            tab = reduce_corruption_to_zero(tab, args, myprint)
        else:

            # do it only for train

            if "train" in this_file and (not args.retain_existing_corruption_for_train):
                # 1st erase all corruption -- we will choose b/w corrupt and clean, instead of corrupt and existing
                print("Train data file: ", this_file, " Reducing corruption to 0 first")
                tab = reduce_corruption_to_zero(tab, args, myprint)

            tab["map"] = tab.apply(
                lambda row: dict(zip(row["retrieved_ids"], row["retrieved_passages"])),
                axis=1,
            )

            tab["corrupt_retrieved_ids"] = tab.apply(
                lambda x: force_retriever_failure(x, args), axis=1
            )
            random.seed(args.seed + ind**2 + ind**3)

            existing_corrupt = 1.0 - tab["in_top5"].mean()

            # with args.corrupt_prob, we sample corrupt_retrieved_ids.
            # But for `existing_corrupt` fraction, both corrupt_retrieved_ids and retrieved_ids are the same and corrupted.
            # therefore, we adjust corrupt_prob to account for this observation
            # for existing_corrupt, coin toss will not have any impact.
            # Let corrupt_prob be the actually coin toss prob.
            # Then, `corrupt_prob*(1 - existing_corrupt)*N + existing_corrupt*N = args.corrupt_prob*N`
            # Therefore, `corrupt_prob = (args.corrupt_prob - existing_corrupt)/(1 - existing_corrupt)`

            # this if block is now redundant after we are reducing corruption to zero before corruption

            if existing_corrupt < args.corrupt_prob:
                corrupt_prob = (args.corrupt_prob - existing_corrupt) / (
                    1 - existing_corrupt
                )
                myprint(
                    "corrupting with prob due to existing corruption: ",
                    corrupt_prob,
                    "\nExisting corruption: ",
                    existing_corrupt,
                )
            else:
                myprint(
                    "existing corrupt is already more than desired corrupt. We won't reduce corruption so that retriever failures remain retriever failures"
                )
                corrupt_prob = 0

            tab["select_corrupt"] = tab.apply(
                lambda row: select_retrieved_ids(
                    row, topk=5, corrupt_prob=corrupt_prob
                ),
                axis=1,
            )

            myprint("fraction of corrupt: ", tab["select_corrupt"].sum() / tab.shape[0])

            tab["selected_ids"] = tab.apply(
                lambda row: row["corrupt_retrieved_ids"]

                if (row["select_corrupt"] == 1)
                else row["retrieved_ids"],
                axis=1,
            )

            tab["retrieved_ids"] = tab["selected_ids"]
            tab["retrieved_passages"] = tab.apply(
                lambda row: [row["map"][x] for x in row["retrieved_ids"]], axis=1
            )
            del tab["map"]

        tab["in_top5"] = tab.apply(
            lambda row: 1

            if (
                len(set(row["retrieved_ids"][:5]).intersection(set(row["int_id_list"])))
                > 0
            )
            else 0,
            axis=1,
        )
        myprint(
            "In top 5 average after corruption:"
        )  # , tab.groupby('in_top5')['question'].describe())
        myprint(tab["in_top5"].mean())
        # del tab["in_top5"]
        keep_cols = original_columns + [
            "orig_retrieved_ids",
            "corrupt_retrieved_ids",
            "in_top5",
        ]
        print(keep_cols)
        tab = tab[[x for x in keep_cols if x in tab.columns]]
        tab.to_json(
            output_file,
            orient="records",
            lines=this_file.endswith("jsonl"),
        )

    myprint("********** END ********")


if __name__ == "__main__":
    main()
