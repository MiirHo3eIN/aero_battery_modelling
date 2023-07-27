# This script dynamically estimates the battery level of the sensor nodes based on the acquisition time and the battery voltage.

# Define the constants

"""
    :param constant_read_energy: The energy consumed by the sensor node when reading the sensors (in mA)
    :param constant_wake_up: The energy consumed by the sensor node when waking up (in mA)
    :param constant_read_time_minutes: The time it takes to read the sensors except for the Mics (in minutes) 
    :param constant_battery_capacity: The capacity of the battery (in mAh)
    :param constant_battery_nominal_energy: The nominal energy of the battery (in mWh) # TODO: Modify 6V based on the nominal battery voltage
"""
constant_read_energy = 10
constant_wake_up = 2
constant_read_time_minutes = 7
constant_battery_capacity = 1000
constant_battery_nominal_energy = (6 - 3.3) * 1000


# Define the scenarios dictionary, values are the current consumption of the sensor node in mA
scenarios = {
    "IMU": 8,
    "Mics": 15,
    "Baros": 28,
    "DiffBaros": 22,
    "IMU + Mics": 16,
    "IMU + DiffBaros": 31,
    "IMU + Baros": 30,
    "Mics + DiffBaros": 31,
    "Mics + Baros": 38,
    "Baros + DiffBaros": 33,
    "IMU + Mics + Baros": 39,
    "IMU + Mics + DiffBaros": 32,
    "IMU + Baros + DiffBaros": 34,
    "Mics + Baros + DiffBaros": 42,
    "IMU + Mics + Baros + DiffBaros": 43
}


def calculate_scenarios(battery_voltage, acquisition_time_minutes, scenarios, periodic_acquisition=False, interval_minutes=0, duration_hours=0, previous_calculation=None):
    # Calculate the possible scenarios based on the battery voltage and acquisition time
    calculations = {}

    if periodic_acquisition:
        number_of_acquisitions = duration_hours / (interval_minutes / 60)
        acquisition_duration_minutes = number_of_acquisitions * acquisition_time_minutes
        acquisition_time_hours = acquisition_duration_minutes / 60
    else:
        acquisition_duration_minutes = acquisition_time_minutes
        acquisition_time_hours = acquisition_time_minutes / 60

    for scenario, value in scenarios.items():
        constant_read_time = constant_read_time_minutes if 'IMU' in scenario or 'DiffBaros' in scenario or 'Baros' in scenario else acquisition_duration_minutes * 10
        
        if previous_calculation is None:
            calculation = (3.3) * (value * acquisition_time_hours + constant_read_time / 60 * constant_read_energy)
        else:
            calculation = previous_calculation + (3.3) * (value * acquisition_time_hours + constant_read_time / 60 * constant_read_energy)
        
        calculations[scenario] = calculation

    battery_capacity_calculation = constant_battery_capacity * (battery_voltage - 3.3)

    
    possible_scenarios = [scenario for scenario, calculation in calculations.items() if calculation < battery_capacity_calculation]


    return possible_scenarios, battery_capacity_calculation, calculations




def main(battery_voltage, acquisition_time_minutes, is_sunny, periodic_acquisition, interval_minutes, duration_hours):
    # This is the main wrapper function of the script
    possible_scenarios, battery_capacity_calculation, calculations = calculate_scenarios(battery_voltage, acquisition_time_minutes, scenarios, periodic_acquisition, interval_minutes, duration_hours)

    if possible_scenarios:
        print("Possible scenarios with the current battery voltage and acquisition time:")
        print(possible_scenarios)
        for scenario in possible_scenarios:
            if periodic_acquisition:
                constant_read_time = constant_read_time_minutes if 'Mics' not in scenario else constant_read_time_minutes * 10
                remaining_battery_energy = battery_capacity_calculation - (3.3 * (((acquisition_time_minutes / 60) * (scenarios[scenario])) + ((constant_read_time / 60) * constant_read_energy)) * (duration_hours / (interval_minutes / 60)))
            else:
                constant_read_time = constant_read_time_minutes if 'Mics' not in scenario else constant_read_time_minutes * 10
                remaining_battery_energy = battery_capacity_calculation - (3.3 * (((acquisition_time_minutes / 60) * (scenarios[scenario])) + ((constant_read_time / 60) * constant_read_energy)))
            
            if is_sunny:
                if periodic_acquisition:
                    constant_read_time = constant_read_time_minutes if 'Mics' not in scenario else constant_read_time_minutes * 10
                    remaining_battery_energy += 33.6 * sunny_time
                else:
                    constant_read_time = constant_read_time_minutes if 'Mics' not in scenario else constant_read_time_minutes * 10
                    remaining_battery_energy += 33.6 * (((constant_read_time + acquisition_time_minutes)/60))

            remaining_battery_percentage = (remaining_battery_energy / constant_battery_nominal_energy) * 100
            remaining_battery_voltage = (remaining_battery_energy / constant_battery_capacity) + 3.3


            if remaining_battery_percentage < 0: 
                remaining_battery_percentage = 0
            if remaining_battery_voltage < 3.3:
                continue

            # Recursive calculation of the number of times scenario can be run
            times_run = 0
            while remaining_battery_energy >= calculations[scenario]:
                remaining_battery_energy -= calculations[scenario]
                times_run += 1

            print(f"{scenario} - Remaining battery level: {remaining_battery_percentage:.2f}% - Remaining battery voltage: {remaining_battery_voltage:.2f}V - Scenario can be repeated: {int(times_run)}")
    else:
        print("No scenarios are possible with the current battery voltage and acquisition time.")

if __name__ == "__main__":
    # User inputs
    battery_voltage = float(input("Enter the battery voltage (V): "))
    acquisition_time_minutes = float(input("Enter the acquisition time (in minutes): "))
    is_sunny = input("Is it sunny? (yes/no): ").lower() == "yes"

    if is_sunny:
        sunny_time = float(input("How much longer is it going to be sunny? (hours) "))

    # Check if periodic acquisition is chosen
    periodic_acquisition = input("Do you want to enable periodic acquisition? (yes/no): ").lower() == "yes"
    if periodic_acquisition:
        interval_minutes = float(input("Enter the interval between acquisitions (in minutes): "))
        duration_hours = float(input("Enter the duration of acquisitions (in hours): "))
    else:
        interval_minutes = 0
        duration_hours = 0

    main(battery_voltage, acquisition_time_minutes, is_sunny, periodic_acquisition, interval_minutes, duration_hours)