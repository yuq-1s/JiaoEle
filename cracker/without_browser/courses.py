def are_overlap(course1, course2):
    def have_overlap(low1, high1, low2, high2):
        low1 = int(low1)
        high1 = int(high1)
        low2 = int(low2)
        high2 = int(high2)
        assert low1 <= high1 and low2 <= high2
        return not (low1 > high2 or low2 > high1)

    for parity in ('odd_week', 'even_week'):
        for c1 in course1.get(parity, {}):
            for c2 in course2.get(parity, {}):
                if c1['weekday'] == c2['weekday'] \
            and have_overlap(c1['wbegin'], c1['wend'], c2['wbegin'],c2['wend'])\
            and have_overlap(c1['cbegin'], c1['cend'], c2['cbegin'],c2['cend']):
                    return True
    return False

def contains(course1, course2):
    def period_contains(p1, p2):
        return p1['weekday'] == p2['weekday'] \
                and int(p1['wbegin']) <= int(p2['wbegin']) \
                and int(p1['wend']) >= int(p2['wend']) \
                and int(p1['cbegin']) <= int(p2['cbegin']) \
                and int(p1['cend']) >= int(p2['cend'])

    for parity in ('odd_week', 'even_week'):
        if not all(any(period_contains(p1, p2) for p1 in course1[parity]) \
                for p2 in course2[parity]):
            return False
    return True

