# JiaoEle

A helper tool for [sjtu course system](http://electsys.sjtu.edu.cn/edu/).

- ~~This is my first attempt to contribute some code on github.~~
- ~~The git log is in a horrible mess. So are branches~~
- ~~I saperated this project into branches but don't know how to merge them.~~
- ~~I have no knowledge on distutils currently.~~

## Installation

**TODO** -- Help! I have no knowledge on distutils now.

Try to meet the following (third-party) dependencies and clone this repository.

- [requests](http://docs.python-requests.org/en/master/)
- [scrapy](https://doc.scrapy.org) for scrapying and parse html course table.
- [numpy](https://github.com/numpy/numpy) An ugly hack in parsing course table.
- [BeautifulSoup](https://pypi.python.org/pypi/beautifulsoup4) for parsing html.
- [PIL](https://github.com/python-pillow/Pillow) for cracking captcha.
- [pytesseract](https://github.com/madmaze/pytesseract) for cracking captcha.
- [xpinyin](https://github.com/lxneng/xpinyin) for course names completion.
- [prettytable](https://github.com/nickl-/prettytable) for course printing.
- [tqdm](https://github.com/tqdm/tqdm) for progress bar in initialization.
- [termcolor](https://github.com/hfeeki/termcolor) for color outputing.

## Usage

> $ python3 main.py `<username>` `<password>`

> $ help

## TODO

- Easy installation.
- Add history in readme.
- Replace pages directory with a pickle.
- def get\_grabbing: print out courses the software is grabbing.
- Cancel / Pause course grabbing.
- Multiple modes: 1. Only query; 2. Query with browser grabbing; 3. Offline
- Functionality when the website is closed: qcurrent, qavai.
- Print course type in print\_course.
- Notify user newly availble courses in real time.
- Reset after unknown exception.
- Store cookies in case jaccount login fails to serve thousands of students.

## FIXME

- I didn't consider thread safety in implementing grabber.py
- Tests are definitely insufficient.

## Contributing

~~As a newbie I have tried my best to make these code readable.~~

Feel free to **fork it!**

## License

MIT License

Copyright (c) 2016 yuq-1s

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
