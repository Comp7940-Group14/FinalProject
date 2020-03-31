import csv


def get_Patient_Distribute_Text(msg):

    # df = pd.read_csv("patients.csv", index=None)
    # text = str(df[:3])

    array = msg.split(' ')
    num = len(array) -1

    text = ''
    temp = ''
    day = 0
    with open("patients.csv" , newline='', encoding='UTF-8') as csvfile:
        rows = csv.reader(csvfile)
        for row in rows:
            if row[0] == "Date":
                text += row[0] + '      ' + row[1] + ' ' + row[2] + "\n"
            else:
                text += row[0] + ' ' + row[1] + '  '+ row[2] + "\n"

            if array[num] == row[1]:
                if day == 1:
                    text = temp + "\n" + row[0] + ' ' + row[1] + ' ' + row[2]
                    break
                temp = row[0] + ' ' + row[1] + ' ' + row[2]
                day = 1

    return text