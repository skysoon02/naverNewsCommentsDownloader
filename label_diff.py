before = set()

with open('./data/newsTitleCum/labeled_until_3_15', 'r', encoding="UTF-8-sig") as file:
    lines = file.readlines()
    for line in lines:
        before.add(line)


after = set()

with open('./data/newsTitleCum/labeled_until_6_25', 'r', encoding="UTF-8-sig") as file:
    lines = file.readlines()
    for line in lines:
        after.add(line)

print(len(before), len(after), len(after)-len(before), len(after-before))

with open('./label', 'w', encoding="UTF-8-sig") as file:
    for line in list(after-before):
        file.write(line)

