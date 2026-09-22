# For the presenter

Not part of the demo and not shown to the client.

- [DEMO_SCRIPT.md](DEMO_SCRIPT.md): the talk track. What to say and show for each prompt, what to do if something goes differently, and answers to likely client questions.
- `verify_step.py` and `check_quotes.py`: checks to rehearse with before the meeting.

## Rehearse

After each prompt, run the check with the number of that prompt, from a terminal in the demo folder:

```bash
python3 presenter/verify_step.py 1    # after "What is going on?" (Ask mode)
python3 presenter/verify_step.py 2    # after the diagnosis
python3 presenter/verify_step.py 3    # after "Is the second pod failing...?" (Ask mode)
python3 presenter/verify_step.py 4    # after the fix
python3 presenter/verify_step.py 5    # after the incident note
python3 presenter/verify_step.py 6    # after the runbook
```

The check confirms that:
- the Ask-mode prompts changed no files
- every `file:line` quote Bob wrote is really on that line
- the fix uses the release-note values and changes nothing else
- the incident note names the owner team and leaves customer impact as `<to fill>`
- the runbook uses only the `kubectl` commands listed in `evidence/README.md` and escalates to the owner team
- `evidence/`, `docs/`, the rule, `scripts/` and `catalog-info.yaml` were not changed

For the two Ask-mode prompts, also read Bob's answer: every fact should name its file and line, and for the second pod Bob should say that `OOMKilled` is likely but not proven.

It uses only Python's standard library. To start again, run the reset prompt in Bob.
