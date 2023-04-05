"""
Assemble and sort some COVID reads...
"""
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from latch import map_task, small_task, workflow
from latch.functions.messages import message
from latch.resources.launch_plan import LaunchPlan
from latch.types import (LatchAuthor, LatchFile, LatchMetadata,
                         LatchParameter)


@dataclass
class Sample:
    name: str
    r1: LatchFile
    r2: LatchFile

@small_task
def assembly_task(sample: Sample) -> LatchFile:

    # A reference to our output.
    sam_file = Path("covid_assembly.sam").resolve()

    bowtie2_cmd = [
        "bowtie2/bowtie2",
        "--local",
        "--very-sensitive-local",
        "-x",
        "wuhan",
        "-1",
        sample.r1.local_path,
        "-2",
        sample.r2.local_path,
        "-S",
        str(sam_file),
    ]

    try:
        # We use shell=True for all the benefits of pipes and other shell features.
        # When using shell=True, we pass the entire command as a single string as
        # opposed to a list since the shell will parse the string into a list
        # using its own rules.
        subprocess.run(" ".join(bowtie2_cmd), shell=True, check=True)
    except subprocess.CalledProcessError as e:
        # will display in the messages tab of the execution graph for the assembly_task node
        message(
            "error",
            {"title": "Bowtie2 Failed", "body": f"Error: {str(e)}"},
        )
        raise e

    # intended output path of the file in Latch console, constructed from
    # the user provided output directory
    output_location = f"latch:///Assembly Outputs/{sample.name}/covid_assembly.sam"

    return LatchFile(str(sam_file), output_location)


"""The metadata included here will be injected into your interface."""
metadata = LatchMetadata(
    display_name="Assemble FastQ Files (Registry Sample Sheet Version)",
    documentation="your-docs.dev",
    author=LatchAuthor(
        name="Author",
        email="author@gmail.com",
        github="github.com/author",
    ),
    repository="https://github.com/your-repo",
    license="MIT",
    parameters={
        "samples": LatchParameter(
            display_name="Sample sheet",
            samplesheet=True,
            description="A list of samples and their sequencing reads",
        )
    },
    tags=[],
)


@workflow(metadata)
def assemble_and_sort(
    samples: List[Sample]
) -> List[LatchFile]:
    """Description...

    markdown header
    ----

    Write some documentation about your workflow in
    markdown here:

    > Regular markdown constructs work as expected.

    # Heading

    * content1
    * content2
    """
    return map_task(assembly_task)(sample=samples)


"""
Add test data with a LaunchPlan. Provide default values in a dictionary with
the parameter names as the keys. These default values will be available under
the 'Test Data' dropdown at console.latch.bio.
"""
LaunchPlan(
    assemble_and_sort,
    "Test Data",
    {
        "samples": [
            Sample(
                r1=LatchFile("s3://latch-public/init/r1.fastq"),
                r2=LatchFile("s3://latch-public/init/r2.fastq"),
                name="test"
            )
        ]
    },
)
