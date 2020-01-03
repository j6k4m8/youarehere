"""
# you are here 🌎

Somehow, adding a new record to Route53 takes 100 lines of Python. So now it
only takes one.

```python
>>> from youarehere import create_record
>>> create_record("A", "foo.example.com", "4.4.4.4")
```

You can also easily point a record to the current machine:

```python
>>> from youarehere import point_record_to_here
>>> point_record_to_here("foo.example.com")
```
"""

from typing import List, Union

import boto3
import requests
import click

# Types of records that you can upload to Route53:
VALID_RECORD_TYPES = [
    "A",
    "AAAA",
    "CAA",
    "CNAME",
    "MX",
    "NAPTR",
    "NS",
    "PTR",
    "SOA",
    "SPF",
    "SRV",
    "TXT",
]
DEFAULT_TTL = 300


def get_global_ip():
    """
    Get the current machine's global IP.

    Arguments:
        None

    Returns:
        str: The machine's global IP

    """
    r = requests.get(r"https://jsonip.com")
    return r.json()["ip"]


def generate_change_json(
    name: str, records: List[str], type: str, ttl: int = 300, comment: str = ""
):
    """
    Generate the AWS-format-friendly JSON/dict for this change request.

    Arguments:
        see create_record

    Returns:
        boto3.Response

    Example:
        name: "a.example.com"
        type: "A"
        comment: "Create a new record"
        records: ["4.4.4.4"]
        ttl: 360

    """
    if type not in VALID_RECORD_TYPES:
        raise ValueError("Type {} is not valid.".format(type))

    return {
        "Comment": str(comment),
        "Changes": [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": str(name),
                    "Type": str(type),
                    "TTL": int(ttl),
                    "ResourceRecords": [{"Value": str(v)} for v in records],
                },
            }
        ],
    }


def guess_hosted_zone_id_for_name(record_name: str) -> str:
    """
    Guess the hosted zone given a record name.

    This does some janky string-matching based upon the FQDN, so if you're
    using this library to create a new record for a domain (rather than a
    subdomain), this match will fail; you should get the hosted zone ID by
    hand instead.

    Arguments:
        record_name (str): The record name to guess the HZ for

    Returns:
        str: A hosted-zone ID in the format "str/str"

    """
    client = boto3.client("route53")
    # Get a list of all HZs:
    hosted_zones = client.list_hosted_zones_by_name().get("HostedZones", [])

    # Figure out which HZ is our new home:
    hosted_zone_id = None
    for zone in hosted_zones:
        if zone["Name"].split(".") == record_name.split(".")[-3:]:
            hosted_zone_id = zone["Id"]
    if hosted_zone_id is None:
        raise ValueError(
            "Could not find an appropriate hosted zone for new "
            + f"record {record_name}. Please specify one explicitly."
        )
    return hosted_zone_id


def create_record(
    record_type: str,
    name: str,
    destination: Union[str, List[str]],
    hosted_zone_id: str = None,
    comment: str = "",
    ttl: int = DEFAULT_TTL,
    dry_run: bool = False,
) -> "boto3.Response":
    """
    Create a new record in Route53.

    Arguments:
        record_type (`str`): The type of the record to add (e.g. `CNAME`).  For
            an exhaustive list, see `youarehere.VALID_RECORD_TYPES`.
        name (`str`): The DNS record name (e.g. `"foo.example.com"`)
        destination (`str` `List[str]`): The destination IP or values (e.g.
            `["4.4.4.4", "8.8.8.8"]`). If you provide a single string, it will
            be treated as an Array[1].
        hosted_zone_id (`str`: None): ID of the hosted zone to which to add
            this record. Guess automatically by default, or you can use
            `youarehere.guess_hosted_zone_id_for_name`.
        comment (`str`: ""): An optional comment for the change request (e.g.
            `"Baby's first DNS record!"`)
        ttl (`int`: 300): The TTL for your record; defaults to 300 which is
            probably too low.
        dry_run (bool: False): If set to True, do not perform the write; just
            return to the user the change request.

    Returns:
        boto3.Response

    """
    # fully-qualify-ify:
    name = name.rstrip(".") + "."

    # Destination must be a list of values:
    if isinstance(destination, str):
        destination = [destination]

    if hosted_zone_id is None:
        try:
            hosted_zone_id = guess_hosted_zone_id_for_name(name)
        except:
            raise ValueError(
                "Could not find an appropriate hosted zone for new "
                + f"record {name}. Please specify one explicitly."
            )

    change_json = generate_change_json(
        name, destination, type=record_type, ttl=ttl, comment=comment
    )
    if dry_run:
        return {"hosted_zone_id": hosted_zone_id, "change": change_json}

    client = boto3.client("route53")
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id, ChangeBatch=change_json
    )
    return response


def point_record_to_here(record_name: str):
    """
    Create a new A record and point it at the current global IP.

    Arguments:
        record_name (str): The record name to assign to this machine

    Returns:
        boto3.Response

    """
    ip = get_global_ip()
    return create_record("A", record_name, [ip])


@click.command()
@click.argument(
    "name",
    # help="Record to add (e.g. 'test.example.com')"
)
@click.argument(
    "destination",
    required=False,
    default=None,
    #help="IP destination. Defaults to the current global IP if none is provided.",
)
@click.option(
    "--type",
    type=click.Choice(VALID_RECORD_TYPES),
    default="A",
    help="The type of the record to add.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print and quit without making changes.",
)
@click.option(
    "--ttl", type = click.INT, default = DEFAULT_TTL,
     help="The TTL for the new record."
)
def cli(name, destination, type, dry_run):
    """
    Examples:

    Point 'test.example.com' to the current machine:

        $ youarehere test.example.com

    Point 'test.example.com' to the IP 93.184.216.34

        $ youarehere test.example.com 93.184.216.34

    Point 'test.example.com' to a set of IPs in descending order,
    with a TTL of 6000 seconds.

        $ youarehere test.example.com 93.184.216.34,93.184.216.35 --ttl 6000
    """

    if destination is None:
        destination = get_global_ip()
    if len(destination.split(",")) > 1:
        destination = [a.strip() for a in destination.split(",")]
    create_record(type, name, destination, dry_run=dry_run)

