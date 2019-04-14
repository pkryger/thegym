* Get notification when there's available session at The Gym

For now The Gym Ealing is hardcoded.

Usage:

```bash
poll.py mydates
```

where `mydates` is a file with dates like:

```
2019-04-15T18:50:00
2019-04-16T09:15:00
```

It returns 0 when NO session is found, and no 0 when there are
sessions found. This is to make it easier to add to Synology
and send e-mails on script failure.

Old dates as well as found dates are removed from the file.
