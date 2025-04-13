import math
import matplotlib.pyplot as plt
from Moon import Moon


def plot_landing(time_log, alt_log, vs_log, hs_log, fuel_log, nn_log):
    plt.figure(figsize=(12, 10))

    # Altitude
    plt.subplot(3, 2, 1)
    plt.plot(time_log, alt_log, label="Altitude (m)", color='skyblue')
    plt.ylabel("Altitude (m)")
    plt.xlabel("Time (s)")
    plt.grid(True)
    plt.legend()

    # Vertical Speed
    plt.subplot(3, 2, 2)
    plt.plot(time_log, vs_log, label="Vertical Speed (m/s)", color='red')
    plt.ylabel("V Speed (m/s)")
    plt.xlabel("Time (s)")
    plt.grid(True)
    plt.legend()

    # Horizontal Speed
    plt.subplot(3, 2, 3)
    plt.plot(time_log, hs_log, label="Horizontal Speed (m/s)", color='orange')
    plt.ylabel("H Speed (m/s)")
    plt.xlabel("Time (s)")
    plt.grid(True)
    plt.legend()

    # Fuel
    plt.subplot(3, 2, 4)
    plt.plot(time_log, fuel_log, label="Fuel (kg)", color='green')
    plt.ylabel("Fuel (kg)")
    plt.xlabel("Time (s)")
    plt.grid(True)
    plt.legend()

    # Throttle (NN)
    plt.subplot(3, 2, 5)
    plt.plot(time_log, nn_log, label="Throttle (NN)", color='purple')
    plt.ylabel("Throttle")
    plt.xlabel("Time (s)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


class Bereshit:
    weight_empty = 165  # kg
    weight_fuel = 420  # kg
    weight_full = weight_empty + weight_fuel

    main_engine_force = 430  # Neutons
    secondadry_engine_force = 25  # Neutons
    main_engine_burn = 0.15  # liter per sec
    secondary_engine_burn = 0.009  # liter per sec
    all_burn = main_engine_burn + 8 * secondary_engine_burn

    @staticmethod
    def compute_acceleration(weight):
        total_force = Bereshit.main_engine_force
        total_force += 8*Bereshit.secondadry_engine_force
        return total_force/weight  # retrograde acceleration to moon's surface

    @staticmethod
    def compute_throttle(vertical_velocity, targetVerticalVel,horizontal_velocity, targetHorizontalVel, weight):
        verticalDeltaV = vertical_velocity - \
            targetVerticalVel  # positive if we're too fast
        horizontalDeltaV = horizontal_velocity -  targetHorizontalVel

        # requiredAcc = verticalDeltaV**2 + horizontalDeltaV**2
        requiredAcc = verticalDeltaV**2
        requiredForce = math.sqrt(requiredAcc) * weight
        maxTotalThrust = Bereshit.main_engine_force + \
            8 * Bereshit.secondadry_engine_force
        throttle = requiredForce / maxTotalThrust
        return max(0, min(1, throttle))


    @staticmethod
    def compute_angle(horizontal_velocity, altitude):
        target_v = Bereshit.target_horizontal_velocity(altitude)
        delta_v = horizontal_velocity - target_v
        if delta_v <= 0:
            return 0
        # Let angle scale more steeply with horizontal excess
        base_angle = min(80, delta_v / 4)
        # Limit angle based on altitude
        if altitude > 8000:
            return min(base_angle, 20)
        elif altitude > 4000:
            return min(base_angle, 35)
        elif altitude > 1500:
            return min(base_angle, 50)
        else:
            return min(base_angle, 85)

    @staticmethod
    def target_vertical_velocity(altitude):
        if (altitude > 2000):
            return 25
        if (altitude > 1000):
            return 15
        if (altitude > 200):
            return 10
        if (altitude > 50):
            return 5
        return 2  # final descent

    @staticmethod
    def target_horizontal_velocity(altitude):
        if altitude > 5000:
            return 600  # it's fine to still go fast
        elif altitude > 2000:
            return 300
        elif altitude > 500:
            return 100
        return 0
    

    def main():
        print("Simulating Bereshit's Landing:")

        vertical_velocity = 24.8  # vertical speed (m/s)
        horizontal_velocity = 932  # horizontal speed (m/s)
        distance_to_land = 181000  # distance to landing site
        angle = 58.3  # landing angle
        altitude = 13748  # altitude
        time = 0  # time in seconds
        delta_time = 1  # time step
        acceleration = 0  # acceleration
        fuel_amount = 121  # fuel amount
        current_weight = Bereshit.weight_empty + fuel_amount
        thrust_power = 0.7  # thrust power factor

        # mathplotlib
        time_log = []
        alt_log = []
        vertV_log = []
        horzV_log = []
        fuel_log = []
        nn_log = []

        while (altitude > 0):


            # ✨ New throttle logic:
            targetVerticalVelocity = Bereshit.target_vertical_velocity(
                altitude)
            targetHoriztontalVelocity = Bereshit.target_horizontal_velocity(
                altitude)
            thrust_power = Bereshit.compute_throttle(
                vertical_velocity, targetVerticalVelocity,horizontal_velocity, targetHoriztontalVelocity, current_weight)
            
            
            #manual-correction
            if altitude < 100 and angle > 10:
                angle -= 7
                thrust_power *=1.1
            elif altitude <50 and angle !=10:
                angle = 10
                thrust_power *=1.5
            elif altitude < 20 and angle != 0:
                angle = 0
                thrust_power *=2
            
            if altitude < 15 and altitude > 10 and vertical_velocity >= 3 and not applied_thrust:
                angle = 0
                thrust_power *= 2.6  # apply a bit more force to slow down
                print("applying thrust 10m<alt<15m!")
                applied_thrust = True
                
            elif altitude < 10 and altitude > 5 and vertical_velocity >=3 and not applied_thrust:
                angle = 0
                thrust_power *= 2.7
                print("applying thrust 5m<alt<10m!")
                applied_thrust = True
                
            elif altitude <10 and altitude >5 and vertical_velocity <=3 and not applied_thrust:
                angle=0
                thrust_power *= 0.6
                print("reducing thrust 5m<alt<10m")
                applied_thrust = True

            if altitude < 5 and vertical_velocity < 3 and not applied_thrust:
                angle = 0
                thrust_power *= 0.11 # feather the engine near surface
                print("killing thrust 5m>alt")
                applied_thrust = True
                
            
            if altitude < 5 and vertical_velocity >= 3 and not applied_thrust:
                angle = 0
                thrust_power *= 0.4
                print("attempting last break!")
                applied_thrust = True

            applied_thrust = False
            # --- Physics ---
            angle_radian = math.radians(angle)
            horizontal_acc = math.sin(angle_radian) * acceleration
            vertical_acc = math.cos(angle_radian) * acceleration
            moon_vert_acc = Moon.get_acc(horizontal_velocity) # constant 1.622
            # need moon horizontal_acc
            time += delta_time

            # Burn and weight update
            dumpedWeight = delta_time * Bereshit.all_burn * thrust_power
            if fuel_amount > 0:
                fuel_amount -= dumpedWeight
                weight = Bereshit.weight_empty + fuel_amount
                acceleration = thrust_power * \
                    Bereshit.compute_acceleration(weight)
            else:
                acceleration = 0

            vertical_acc -= moon_vert_acc
            if (horizontal_velocity > 0):
                horizontal_velocity -= horizontal_acc * delta_time
            distance_to_land -= horizontal_velocity * delta_time
            vertical_velocity -= vertical_acc * delta_time
            altitude -= delta_time * vertical_velocity

            

            time_log.append(time)
            alt_log.append(altitude)
            vertV_log.append(vertical_velocity)
            horzV_log.append(horizontal_velocity)
            fuel_log.append(fuel_amount)
            nn_log.append(thrust_power)

            if time % 10 == 0 or altitude < 100:
                print(f"{time}, VS: {vertical_velocity:.2f}, HS: {horizontal_velocity:.2f}, ALT: {altitude:.2f}, ANG: {angle:.1f}, FUEL: {fuel_amount:.2f}, NN: {thrust_power:.2f}")

        # after the loop, plrint the results
        plot_landing(time_log, alt_log, vertV_log, horzV_log, fuel_log, nn_log)
        print("\n=== Landing Report ===")
        print(f"Final Altitude: {altitude:.2f} m")
        print(f"Final Vertical Speed: {vertical_velocity:.2f} m/s")
        print(f"Final Horizontal Speed: {horizontal_velocity:.2f} m/s")
        print(f"Remaining Fuel: {fuel_amount:.2f} kg")
        if vertical_velocity < 2 and horizontal_velocity < 2:
            print("✅ Successful landing!")
        else:
            print("💥 Crash landing. Try again.")


if __name__ == "__main__":
    Bereshit.main()
