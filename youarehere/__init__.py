from typing import List, Union

import boto3
import requests

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


def get_global_ip():
    """
    Get the current machine's global IP.
    """
    r = requests.get(r"https://jsonip.com")
    return r.json()["ip"]


def generate_change_json(
    name: str, records: List[str], type: str, ttl: int = 300, comment: str = ""
):
    """
    Example args:
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
            f"Could not find an appropriate hosted zone for new record {record_name}. Please specify one explicitly."
        )
    return hosted_zone_id


def create_record(
    record_type: str,
    name: str,
    destination: Union[str, List[str]],
    hosted_zone_id: str = None,
    comment: str = "",
    ttl: int = 300,
):
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
                f"Could not find an appropriate hosted zone for new record {name}. Please specify one explicitly."
            )

    client = boto3.client("route53")
    response = client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch=generate_change_json(
            name=name, records=destination, type=record_type, ttl=ttl, comment=comment
        ),
    )
    return response


def point_record_to_here(record_name: str):
    """
    Create a new A record and point it at the current global IP.
    """
    ip = get_global_ip()
    return create_record("A", record_name, [ip])


"""
Example:

>>> create_record("A", "foo.example.com", "4.4.4.4")

>>> point_record_to_here("foo.example.com")
"""
