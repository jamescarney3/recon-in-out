## YCharts Coding Challenge Q3
This example uses no external dependencies and should run as-is on any machine
with python installed.

I've included a sample `recon.in` text file in the top level directory for
`recon.py` to process for default behavior, but it will also process any other
properly formatted local file if that file's absolute path is passed as a second
positional argument when `recon.py` is run.


#### How to run:
- Clone this repo

`git clone git@github.com:jamescarney3/recon-in-out.git`
- In parent directory, run main script to process example recon.in file

`python recon.py`
- Output is written to top level `recon.out` text file
- Optionally run with an absolute path as second positional argument to process
a recon.in formatted text file at that path