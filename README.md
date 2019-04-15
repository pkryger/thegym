* Get notification when there's available session at The Gym

For now The Gym Ealing is hardcoded.

Usage:

```bash
python3 poll.py --email someone@somewhere --path mydates
```

where `mydates` is a path to a file with dates in the following format:

```
2019-04-15T18:50:00
2019-04-16T09:15:00
```

It requires a `~/.netrc` file with a section for `smtp.gmail.com`.

Old dates as well as found dates are removed from the file.
