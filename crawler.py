import logging
from pathlib import Path
from typing import Dict, List

import click
from git import Repo

logging.basicConfig(
    format="%(asctime)s - %(levelname)-8s %(filename)s:%(lineno)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger(__name__)


def fetch_matched_lines(file_path: Path, pattern: str) -> Dict[int, str]:
    """
    Returns all lines in file matched the pattern with their line numbers
    """
    with file_path.open() as f:
        return {
            index: line.rstrip()
            for index, line in enumerate(f.readlines(), start=1)
            if pattern in line
        }


def make_line_git_url(
    repo: Repo, repo_url: str, file_rel_path: Path, line_index
) -> str:
    return (
        f"{repo_url}/blob/{repo.active_branch.name}/{str(file_rel_path)}#L{line_index}"
    )


def blame_file(
    repo: Repo,
    repo_url: str,
    repo_dir: Path,
    file_path: Path,
    lines: Dict[int, str],
    is_verbose_output: bool,
) -> List[str]:
    blames = []

    for line_index, line in lines.items():
        res = repo.blame(rev="HEAD", file=str(file_path), L=f"{line_index},+1")
        assert len(res) == 1, "Expected one and only one last commit for the line"

        commit = res[0][0]

        line_git_url = make_line_git_url(
            repo, repo_url, file_path.relative_to(repo_dir), line_index
        )

        blame_info = (
            f"author={commit.author}, "
            f"git_url={line_git_url}"
        )
        if is_verbose_output:
            blame_info += f", revision={commit.hexsha}"
        logger.info(f"\t{blame_info}")

        blames.append(blame_info)

    return blames


@click.command(help="Tool for finding authors of the code changes")
@click.option("-ru", "--repo-url", required=True, help="Git repo URL")
@click.option(
    "-rp",
    "--repo-path",
    required=True,
    type=Path,
    help="Path to local Git repo where do searching",
)
@click.option(
    "-d",
    "--dir-path",
    required=True,
    type=Path,
    help="Dir in Git repo where do searching (relative path)",
)
@click.option(
    "-s",
    "--search-pattern",
    required=True,
    help="Search pattern (regexp is not supported)",
)
@click.option(
    "-e",
    "--supported-file-extensions",
    default="",
    help="List of file extentions supported for search, separated by comma. Like '.h,.cpp'",
)
@click.option(
    "-o",
    "--output-path",
    type=Path,
    default=Path("./crawler_output.txt"),
    help="Dir in Git repo where do searching (relative path)",
)
@click.option(
    "-v",
    "--verbose",
    type=bool,
    default=False,
    help="Control verbosity of output format",
)
def run(
    repo_url: str,
    repo_path: Path,
    dir_path: Path,
    search_pattern: str,
    supported_file_extensions: str,
    output_path: Path,
    verbose: bool,
):
    repo_path = repo_path.absolute()
    repo = Repo(repo_path)
    root_path = repo_path / dir_path
    supported_extensions = supported_file_extensions.split(",")

    with output_path.open("w") as output_file:
        for file_path in root_path.glob("**/*"):
            if not file_path.is_file():
                continue

            if supported_extensions and file_path.suffix not in supported_extensions:
                continue

            logger.debug(f"Processing file {file_path}")

            matches = fetch_matched_lines(file_path, search_pattern)

            if matches:
                blame_data = blame_file(
                    repo, repo_url, repo_path, file_path, matches, verbose
                )
                output_file.writelines("\n".join(blame_data))
                output_file.write("\n")


if __name__ == "__main__":
    run()
