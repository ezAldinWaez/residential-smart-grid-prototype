SCENARIO_EVENTS = [
    # Morning routine (6-9 AM)
    (1.0, lambda hs: hs.get_house(0).get_device('WATER_HEATER').toggle_envelope_state(0, 1.0)),    # House 1 morning shower
    (1.5, lambda hs: hs.get_house(1).get_device('MICROWAVE').toggle_envelope_state(0, 1.5)),       # House 2 breakfast
    (2.0, lambda hs: hs.get_house(2).get_device('DISHWASHER').toggle_envelope_state(0, 2.0)),      # House 3 morning dishes
    (2.5, lambda hs: hs.get_house(0).get_device('MICROWAVE').toggle_envelope_state(0, 2.5)),       # House 1 breakfast
    # Mid-day activity (10 AM - 2 PM)
    (3.0, lambda hs: hs.get_house(1).get_device('WASHING_MACHINE').toggle_envelope_state(0, 3.0)),  # House 2 laundry
    (4.5, lambda hs: hs.get_house(2).get_device('HVAC').toggle_envelope_state(0, 4.5)),            # House 3 AC on (hot day)
    (5.0, lambda hs: hs.get_house(0).get_device('HVAC').toggle_envelope_state(0, 5.0)),            # House 1 AC on
    (6.0, lambda hs: hs.get_house(1).get_device('MICROWAVE').toggle_envelope_state(0, 6.0)),       # House 2 lunch
    # Afternoon peak (2-6 PM)
    (7.0, lambda hs: hs.get_house(2).get_device('WATER_HEATER').toggle_envelope_state(0, 7.0)),    # House 3 hot water
    (8.0, lambda hs: hs.get_house(1).get_device('HVAC').toggle_envelope_state(0, 8.0)),            # House 2 AC on
    (9.0, lambda hs: hs.get_house(0).get_device('DISHWASHER').toggle_envelope_state(0, 9.0)),      # House 1 dishes
    (9.5, lambda hs: hs.get_house(1).get_device('DRYER').toggle_envelope_state(0, 9.5)),           # House 2 dryer
    # Evening routine (6-10 PM)
    (10.0, lambda hs: hs.get_house(2).get_device('MICROWAVE').toggle_envelope_state(0, 10.0)),     # House 3 dinner prep
    (10.5, lambda hs: hs.get_house(1).get_device('TV').toggle_envelope_state(0, 10.5)),            # House 2 evening TV
    (11.0, lambda hs: hs.get_house(0).get_device('WATER_HEATER').toggle_envelope_state(0, 11.0)),  # House 1 evening shower
    (12.0, lambda hs: hs.get_house(2).get_device('DISHWASHER').toggle_envelope_state(0, 12.0)),    # House 3 dinner cleanup
    # Night routine and device shutdowns (10 PM - 12 AM)
    (14.0, lambda hs: hs.get_house(0).get_device('HVAC').toggle_envelope_state(0, 14.0)),          # House 1 AC off
    (15.0, lambda hs: hs.get_house(1).get_device('HVAC').toggle_envelope_state(0, 15.0)),          # House 2 AC off
    (15.5, lambda hs: hs.get_house(1).get_device('DRYER').toggle_envelope_state(0, 15.5)),         # House 2 dryer off
    (16.0, lambda hs: hs.get_house(2).get_device('HVAC').toggle_envelope_state(0, 16.0)),          # House 3 AC off
    # Late evening/early morning
    (18.0, lambda hs: hs.get_house(1).get_device('TV').toggle_envelope_state(0, 18.0)),            # House 2 TV off
    (20.0, lambda hs: hs.get_house(0).get_device('MICROWAVE').toggle_envelope_state(0, 20.0)),     # House 1 late snack
]
