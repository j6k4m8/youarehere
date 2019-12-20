## *Function* `get_global_ip()`


Get the current machine's global IP.

### Arguments
    None

### Returns
> - **str** (`None`: `None`): The machine's global IP



## *Function* `guess_hosted_zone_id_for_name(record_name: str) -> str`


Guess the hosted zone given a record name.

This does some janky string-matching based upon the FQDN, so if you're using this library to create a new record for a domain (rather than a subdomain), this match will fail; you should get the hosted zone ID by hand instead.

### Arguments
> - **record_name** (`str`: `None`): The record name to guess the HZ for

### Returns
> - **str** (`None`: `None`): A hosted-zone ID in the format "str/str"



## *Function* `point_record_to_here(record_name: str)`


Create a new A record and point it at the current global IP.

### Arguments
> - **record_name** (`str`: `None`): The record name to assign to this machine

### Returns
    boto3.Response

