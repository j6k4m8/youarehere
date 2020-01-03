# you are here 🌎

![PyPI - License](https://img.shields.io/pypi/l/youarehere?style=for-the-badge) ![PyPI](https://img.shields.io/pypi/v/youarehere?style=for-the-badge) ![](https://img.shields.io/badge/PRETTY%20DOPE-👍-blue?style=for-the-badge)

Somehow, adding a new record to Route53 takes 100 lines of Python. So now it only takes one.

```python
>>> from youarehere import create_record
>>> create_record("A", "foo.example.com", "4.4.4.4")
```

You can also easily point a record to the current machine:

```python
>>> from youarehere import point_record_to_here
>>> point_record_to_here("foo.example.com")
```

## use case

You have a Raspberry Pi that travels around and you want to keep a pointer to it in Route53. Add this as a cron-job:

```
$ python3 -c "point_record_to_here('my-pi.example.com')"
```


## `create_record` Arguments

| Argument       | Type                | Default | Description                                                                                                                           |
| -------------- | ------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| record_type    | `str`               |         | The type of the record to add (e.g. A, CNAME, etc). For an exhaustive list, see `youarehere.VALID_RECORD_TYPES`.                      |
| name           | `str`               |         | The DNS record name (e.g. `"foo.example.com"`)                                                                                        |
| destination    | `str` / `List[str]` |         | The destination IP or values (e.g. `["4.4.4.4", "8.8.8.8"]`). If you provide a single string, it will be treated as an Array[1].      |
| hosted_zone_id | `str`               | None    | ID of the hosted zone to which to add this record. Guess automatically by default, or use `youarehere.guess_hosted_zone_id_for_name`. |
| comment        | `str`               | ""      | An optional comment for the change request (e.g. `"Baby's first DNS record!"`)                                                        |
| ttl            | `int`               | 300     | The TTL for your record; defaults to 300 which is probably too low.                                                                   |

---

<small>Documentation auto-generated with [`docshund`](https://github.com/FitMango/docshund/), bork bork. 🐕</small>


## CLI Usage

Examples:

Point 'test.example.com' to the current machine:

    $ youarehere test.example.com

Point 'test.example.com' to the IP 93.184.216.34

    $ youarehere test.example.com 93.184.216.34

Point 'test.example.com' to a set of IPs in descending order,
with a TTL of 6000 seconds.

    $ youarehere test.example.com 93.184.216.34,93.184.216.35 --ttl 6000


| Argument    | Description                                 |
| ----------- | ------------------------------------------- |
| name        | Record to add (e.g. "test.example.com")     |
| destination | IP destination. Default: Current global IP. |

| Flag      | Description                                   |
| --------- | --------------------------------------------- |
| --type    | (A) The type of record to add                 |
| --ttl     | (300) The TTL of the new DNS record           |
| --dry-run | (False) Print and quit without making changes |
