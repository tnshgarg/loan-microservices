def convert_to_inr(number):
    s = str(number)
    if len(s) <= 3:
        return s
    else:
        initial = s[:-3]
        last_three = s[-3:]
        formatted_initial = ','.join([initial[i:i+2]
                                     for i in range(0, len(initial), 2)])
        return formatted_initial + ',' + last_three
