examples = [
    ("20161207132431", "https://web.archive.org/web/20161207132431/http://www.fri.uni-lj.si:80/en/"),
    ("20170129015754", "https://web.archive.org/web/20170129015754/https://www.fri.uni-lj.si/en/"),
    ("20170922110659", "https://web.archive.org/web/20170922110659/https://fri.uni-lj.si/en"),
    ("20171027125058", "https://web.archive.org/web/20171027125058/https://www.fri.uni-lj.si/en")
]

for old, new in zip(examples, examples[1::]):
    print(old, new)