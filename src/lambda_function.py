from Schedule import Schedule

def handler(event, context):
    Schedule(
        kid="Ben",
        sport="⚽ Soccer",
        division=6,
        team="Spirits",
    ).save()