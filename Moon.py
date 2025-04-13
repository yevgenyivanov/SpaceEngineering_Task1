class Moon:
    RADIUS = 3475 * 1000  # meters
    ACC = 1.622  # m/s^2
    EQ_SPEED = 1700  # m/s

    @staticmethod
    def get_acc(speed):
        n = abs(speed) / Moon.EQ_SPEED
        return (1 - n) * Moon.ACC
    
if __name__ == "__main__":
    print(Moon.get_acc(932))