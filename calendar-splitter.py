
import argparse
import icalendar

shortHand = {
    'Competências Comunicacionais em Engenharia Informática e de Computadores I': 'CCEIC-I',
    'Competências Comunicacionais em Engenharia Informática e de Computadores II': 'CCEIC-II',
    # Add your own subjects here
}

toShortHandClass = {
    'Laboratorial': 'L',
    'Problemas': 'P',
    'Teórica': 'T',
    'TeoricoPrática': 'TP',
}

def transform(summary: str):
    '''
    summary is like:
    <Subject> : <Type of class>

    returns:
    [{shortHand[<Subject>]}] : {shortHandClass[<Type of class>]}
    '''
    return '[{}] : {}'.format(shortHand[summary.split(':')[0].strip()], toShortHandClass[summary.split(':')[1].strip()])


# Parse command line arguments
parser = argparse.ArgumentParser(description='Split ISTs all-classes calendar into subject specific calendars.')
parser.add_argument('main_calendar', metavar='MAIN_CALENDAR', type=str, help='Path to the all-classes calendar file (.ics)')
args = parser.parse_args()

# Read the main calendar file
with open(args.main_calendar, 'rb') as f:
    main_calendar = icalendar.Calendar.from_ical(f.read())

with open('base.ics', 'rb') as f:
    base_calendar = icalendar.Calendar.from_ical(f.read())


events = dict({
    event.get('summary').split(':')[0].strip(): icalendar.Calendar.from_ical(base_calendar.to_ical()) for event in main_calendar.subcomponents if event.name == 'VEVENT'
})

done = []

for component in main_calendar.subcomponents:
    if component.name == 'VEVENT' and component.get('summary').split(':')[0].strip() not in done:
        summary = component.get('summary').split(':')[0].strip()
        if summary not in shortHand:
            done.append(summary)
            continue
        calendar = events[summary]
        for component2 in main_calendar.subcomponents:
            if component2.name == 'VEVENT':
                if component2.get('summary').split(':')[0].strip() == summary:
                    component2['summary'] = transform(component2['summary'])
                    calendar.add_component(component2)
        with open('subcalendars/' + shortHand[summary] + '.ics', 'wb') as f:
            f.write(calendar.to_ical())
        done.append(summary)
