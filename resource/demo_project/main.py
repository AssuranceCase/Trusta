import math

# Global variable g: gravitational acceleration in meters/second^2, default value is 9.8
g = 10

class Cannon:
    def __init__(self, M, m, alpha, v, k):
        """
        Initialize cannon parameters
        :param M: Mass of the cannon carriage in kilograms
        :param m: Mass of the cannonball in kilograms
        :param alpha: Elevation angle of the cannon in degrees
        :param v: Initial velocity of the cannonball in meters/second
        :param k: Resistance coefficient
        """
        self.M = M
        self.m = m
        self.alpha = math.radians(alpha)  # Convert angle to radians
        self.v = v
        self.k = k

    def is_soldier_safe(self, steps, step_length = 0.7):
        """
        Determine if the soldier is safe at the specified distance behind the cannon carriage
        :param steps: Number of steps taken by the soldier
        :param step_length: Step length of the soldier in meters
        :return: Boolean indicating safety
        """
        # Distance the cannon moves backward
        recoil_distance = self.calculate_recoil_distance()
        # Distance behind the cannon carriage
        distance_behind = self.calculate_distance_behind(steps, step_length) # Distance of the soldier from the cannon carriage in meters
        print(f"The soldier is {distance_behind:.2f} meters behind the cannon after {steps} steps")
        # Safety check
        is_safe = (recoil_distance <= distance_behind)
        return is_safe

    def calculate_recoil_velocity(self):
        """
        Calculate the recoil velocity of the cannon carriage
        :return: Recoil velocity of the cannon carriage in meters/second
        """
        V = (self.m * self.v * math.cos(self.alpha)) / self.M
        return V

    def calculate_recoil_distance(self):
        """
        Calculate the recoil distance of the cannon carriage
        :return: Recoil distance of the cannon carriage in meters
        """
        V = self.calculate_recoil_velocity()
        print(f"Initial recoil velocity V = {V} m/s")
        F_r = self.calculate_resistance(self.k)
        print(f"Resistance on horizontal ground F_r = {F_r} Newtons")

        # The kinetic energy of the cannon carriage equals the work done by the resistance, (V ** 2) * self.M / 2 == F_r * X
        X = (V ** 2) * self.M / 2 / F_r
        print(f"Recoil distance X = {X:.2f} meters")
        return X
    
    def calculate_resistance(self, k):
        """
        Calculate the resistance on horizontal ground
        :return: Resistance in Newtons
        """
        resistance = k * self.M * g
        return resistance
    
    def calculate_distance_behind(self, steps, step_length):
        """
        Calculate the distance of the soldier from the cannon carriage.
        :param steps: Number of steps taken by the soldier.
        :param step_length: Length of each step in meters.
        :return: Distance of the soldier from the cannon carriage in meters.
        """
        distance_behind = steps * step_length
        return distance_behind

if __name__ == '__main__':
    # Create a cannon object and determine if the soldier is safe 2 steps behind the cannon carriage
    cannon = Cannon(M=2000, m=10, alpha=0, v=600, k=0.3)
    is_safe = cannon.is_soldier_safe(steps=2)

    print(f"Is the soldier behind the cannon carriage safe: {'Safe' if is_safe else 'Not Safe'}")
