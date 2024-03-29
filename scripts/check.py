#!/usr/bin/env python3.8
import argparse
import dataclasses
import glob
import io
import pathlib
import re
import sys
import typing
from typing import List, Optional, Union

MODULE_PATH = pathlib.Path(__file__).parent.resolve()


@dataclasses.dataclass
class Token:
    """Token base class, making up a PVList."""

    line: str
    lineno: int

    @classmethod
    def from_line(cls, line, lineno):
        return cls(line=line, lineno=lineno)


@dataclasses.dataclass
class Setting(Token):
    """A token representing a configuration setting."""

    SETTINGS = {
        "evaluation",
    }

    line: str
    setting: Optional[str] = None
    values: Optional[List[str]] = None

    @classmethod
    def from_line(cls, line, lineno):
        setting, *values = line.split(" ")
        return cls(line=line, lineno=lineno, setting=setting, values=values)


@dataclasses.dataclass
class Comment(Token):
    """A token representing a comment line."""


@dataclasses.dataclass
class Expression(Token):
    """A token with a valid regular expression."""

    expr: str
    details: List[str]
    regex: typing.Pattern

    @classmethod
    def from_line(cls, line, lineno):
        line = line.replace("\t", " ")
        expr, *details = line.split(" ")
        try:
            regex = re.compile(expr)
        except Exception as ex:
            return BadExpression(
                line=line, lineno=lineno, expr=expr, details=details, exception=ex
            )
        return cls(line=line, lineno=lineno, expr=expr, details=details, regex=regex)

    def match(self, name):
        if self.regex is not None:
            return self.regex.match(name)


@dataclasses.dataclass
class BadExpression(Token):
    """A token with a bad regular expression."""

    expr: str
    details: str
    exception: Exception


@dataclasses.dataclass
class PVList:
    """A PVList container."""

    identifier: Optional[str] = None
    tokenized_lines: Optional[List[Token]] = None

    def find(self, cls: typing.Type):
        context = None
        for line in self.tokenized_lines:
            if isinstance(line, Comment):
                context = line
            elif isinstance(line, cls):
                yield context, line

    def match(self, name):
        context = None
        for context, expr in self.find(Expression):
            m = expr.match(name)
            if m:
                yield context, expr

    @staticmethod
    def tokenize(line, lineno=0):
        line = line.strip()
        if not line:
            return
        if line.startswith("#"):
            return Comment.from_line(line, lineno=lineno)
        word, *_ = line.split(" ")
        if word.lower() in Setting.SETTINGS:
            return Setting.from_line(line, lineno=lineno)
        # if '*' not in word and ':' not in word:
        #     print('hmm', line)
        return Expression.from_line(line, lineno=lineno)

    @classmethod
    def from_file_obj(cls, fp, identifier=None):
        lines = []
        for lineno, line in enumerate(fp.read().splitlines(), 1):
            tok = PVList.tokenize(line, lineno=lineno)
            if tok is not None:
                lines.append(tok)
        return cls(identifier, lines)

    @classmethod
    def from_file(cls, fn):
        with open(fn, "rt") as fp:
            return cls.from_file_obj(fp, identifier=fn.name)


def create_arg_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="pvlist name matching and linting tool",
    )
    parser.add_argument("--lint", action="store_true", help="Lint regular expressions")
    parser.add_argument(
        "--pvlists",
        type=str,
        nargs="*",
        help="Specific pvlists to check (empty for all)",
    )
    parser.add_argument(
        "--hide-context", action="store_true", help="Hide comment context"
    )
    parser.add_argument(
        "--remove-any", action="store_true", help="Remove '.*' from results"
    )
    parser.add_argument("names", nargs="*", type=str, help="PV names to match")
    return parser


def load_pvlists(pvlists: Optional[List[str]]) -> List[PVList]:
    """
    Load .pvlist files, given their filenames.

    Parameters
    ----------
    pvlists : Optional[List[str]]
        The .pvlist filenames.
        In the case of None, use ``../config/*.pvlist``.

    Returns
    -------
    List[PVList]:
        PVList instances from the files, if successful.
    """
    if pvlists is None:
        pvlists = list((MODULE_PATH.parent / "config").glob("*.pvlist"))
    return [PVList.from_file(fn) for fn in pvlists]


def run_lint(pvlists: List[PVList], show_context=False):
    """
    Lint the given PVLists, looking for invalid regular expressions.

    Parameters
    ----------
    pvlists : List[PVList]
        The PVLists to check
    show_context : bool, optional
        Show comment context for bad lines.
    """
    context = None
    for pvlist in pvlists:
        for context, expr in pvlist.find(BadExpression):
            print_match(pvlist, context, expr, show_context=show_context)


def print_match(
    pvlist: PVList,
    context: Optional[Comment],
    expr: Union[Expression, BadExpression],
    show_context: bool = True,
    file=sys.stdout,
):
    """
    Print a match to stdout.

    Parameters
    ----------
    pvlist : PVList
        The PVList container.
    context : Optional[Comment]
        The comment context of the match.
    expr : Union[Expression, BadExpression]
        The expression that matched.
    show_context : bool
        Option to show or hide context.
    file : file-like object

    """
    ident = pvlist.identifier
    if context is not None and show_context:
        ctx = f" <<Comment: {ident}:{context.lineno}: {context.line}>>"
    else:
        ctx = ""

    print(
        f"{ident}:{expr.lineno}: {expr.expr!r} {' '.join(expr.details)}{ctx}", file=file
    )
    if isinstance(expr, BadExpression):
        print(
            f"{ident}:{expr.lineno}: {expr.expr!r}: ERROR: {expr.exception}", file=file
        )


def run_match_and_aggregate(
    pvlists: List[PVList],
    names: List[str],
    show_context: bool = True,
    remove_any: bool = False,
):
    """
    Match ``names`` against all PVLists, and aggregate by matching rule sets.

    Parameters
    ----------
    pvlists : List[PVList]
        The list of PVLists.
    name : List[str]
        PV name to match.
    show_context : bool
        Show comment context of the matching line.
    remove_any : bool
        Remove catch-all '.*' from lines.
    """
    by_name = {}
    for name in names:
        with io.StringIO() as fp:
            for pvlist in pvlists:
                for context, expr in pvlist.match(name):
                    if expr.expr == ".*" and remove_any:
                        continue

                    print_match(
                        pvlist, context, expr, show_context=show_context,
                        file=fp
                    )

            by_name[name] = fp.getvalue() or "No matches"

    by_rule = {}
    for name, rules in by_name.items():
        if rules not in by_rule:
            by_rule[rules] = set()
        by_rule[rules].add(name)

    for rule, names in by_rule.items():
        print("-" * max(len(line) for line in rule.splitlines()))
        print(rule.strip())
        print("-" * max(len(line) for line in rule.splitlines()))
        for name in sorted(names):
            print(name)
        print()

    return by_rule


def run_match(
    pvlists: List[PVList],
    name: str,
    show_context: bool = True,
    remove_any: bool = False,
):
    """
    Match ``name`` against all PVLists.

    Parameters
    ----------
    pvlists : List[PVList]
        The list of PVLists.
    name : List[str]
        PV name to match.
    show_context : bool
        Show comment context of the matching line.
    remove_any : bool
        Remove catch-all '.*' from lines.
    """
    for pvlist in pvlists:
        for context, expr in pvlist.match(name):
            if expr.expr == ".*" and remove_any:
                continue

            print_match(pvlist, context, expr, show_context=show_context)


def main(lint=False, pvlists=None, names=None, hide_context=False, remove_any=False):
    if not names and not lint:
        print("Nothing to do; did you mean to --lint or forget PV names?",
              file=sys.stderr)
        print(file=sys.stderr)
        _main(["--help"])
        return

    pvlists = load_pvlists(pvlists)
    if lint:
        run_lint(pvlists, show_context=not hide_context)
    if names:
        if len(names) == 1:
            return run_match(
                pvlists=pvlists,
                name=names[0],
                show_context=not hide_context,
                remove_any=remove_any,
            )
        return run_match_and_aggregate(
            pvlists=pvlists,
            names=names,
            show_context=not hide_context,
            remove_any=remove_any,
        )


def _main(args=None):
    parser = create_arg_parser()
    args = parser.parse_args(args or sys.argv[1:])
    main(**vars(args))


if __name__ == "__main__":
    _main()
