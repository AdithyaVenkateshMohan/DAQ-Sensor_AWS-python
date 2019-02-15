import serial.tools.list_ports as list_ports
import time
import serial
import numpy
import struct

# Color conventions
# Green connected
# Yellow upload call
# Blue measurement
# White Charge
# switch off after each command

class Sonar:
    def __init__(self):
        self.id = id(self)
        self.product_key = 'FT231X USB UART'
        self.baud_rate = 3e6
        self.vcc = 3.3

        self.dac_n_samples = 1000
        self.dac_sample_freq = 3.6e5
        self.dac_buildup_cnt = 20

        self.adc_n_samples = 7000
        self.adc_sample_freq = 3.0e5
        self.adc_n_channels = 2
        self.adc_n_bits = 12

        self.connection = None

    @property
    def time(self):
        duration = self.adc_n_samples / self.adc_sample_freq
        time_steps = numpy.linspace(0, duration, self.adc_n_samples) * 1000
        return time_steps

    def write(self, command):
        command = command.encode('utf-8')
        self.connection.write(command)
        self.connection.flushInput()
        self.connection.flushOutput()
        time.sleep(0.1)

    def find_port(self, key=False):
        if not key: key = self.product_key
        ports = list_ports.comports()
        for port in ports:
            if key in str(port.product): return port.device
        return False

    def connect(self, port=False):
        if not port: port = self.find_port()
        if not port: return False
        self.connection = serial.Serial(port, self.baud_rate)
        self.connection.rtscts = True
        self.connection.timeout = 10
        while self.connection.isOpen(): self.connection.close()
        self.connection.open()
        self.connection.flushInput()
        self.connection.flushOutput()
        self.initialize()
        self.blink(color='green')
        return True

    def initialize(self):
        self.set_adc()
        self.set_dac()

    def disconnect(self):
        try:
            self.connection.close()
        except:
            pass

    def set_dac(self, rate=None, samples=None):
        if rate is not None: self.dac_sample_freq = int(rate)
        if samples is not None: self.dac_n_samples = int(samples)
        command1 = '!A,%d,0,0\n' % self.dac_sample_freq
        command2 = '!C,%d,0,0\n' % self.dac_n_samples
        self.write(command1)
        self.write(command2)

    def set_adc(self, rate=None, samples=None):
        if rate is not None: self.adc_sample_freq = int(rate)
        if samples is not None: self.adc_n_samples = int(samples)
        command1 = '!B,%d,0,0\n' % self.adc_sample_freq
        command2 = '!D,%d,0,0\n' % self.adc_n_samples
        self.write(command1)
        self.write(command2)

    def blink(self, color='white', interval=0.1, times=3):
        for cnt in range(times):
            self.set_led(color)
            time.sleep(interval)
            self.set_led('off')
            time.sleep(interval)

    def build_charge(self):
        self.set_led('white')
        command = '!H,0,0,0\n'
        for x in range(0, self.dac_buildup_cnt):
            self.write(command)
            time.sleep(0.1)
        self.set_led('off')

    def set_fm_sweep(self, start_frequency, end_frequency):
        amplitude = 1.40
        command = '!F,%d,%d,%0.2f\n' % (start_frequency, end_frequency, amplitude)
        self.write(command)

    def set_signal(self, start_frequency=75000, end_frequency=25000, length=1000):
        self.set_led('yellow')
        self.set_dac(samples=length)
        self.set_fm_sweep(start_frequency, end_frequency)
        self.set_led('off')

    def set_led(self, color):
        number = 1000
        if color == 'off': number = 0
        if color == 'red': number = 1
        if color == 'green': number = 2
        if color == 'yellow': number = 3
        if color == 'blue': number = 4
        if color == 'magenta': number = 5
        if color == 'cyan': number = 6
        if color == 'white': number = 7
        if number == 1000: return
        command = '!J,%d,0,0\n' % number
        self.write(command)

    def measure(self):
        self.set_led('blue')
        bytes_to_read = self.adc_n_samples * self.adc_n_channels * 2
        command = '!G,0,0,0\n'
        self.write(command)
        data = self.connection.read(bytes_to_read)
        self.set_led('off')
        return data

    def text_command(self, command):
        if not type(command) == list: command = command.split(',')
        colors = ['off', 'white', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']
        if command[0] in colors:
            self.set_led(command[0])
            return True
        if command[0] == 'measure':
            data = self.measure()
            return data
        if command[0] == 'call':
            start_freq = int(command[1])
            end_freq = int(command[2])
            length = int(command[3])
            self.set_signal(start_frequency=start_freq,end_frequency=end_freq,length=length)
            return True
        if command[0] == 'charge':
            self.build_charge()

def convert_data(data, samples=7000):
    channels = 2
    data_format = str(samples * channels) + 'H'
    #for debug must remove later
    #data value seems to be null
    #have to check
    if(data == None):
        print('there is null prob with the Data')
    print(data_format)
    data = numpy.asarray(struct.unpack(data_format, data))
    data = data.reshape((samples, channels))
    means = numpy.mean(data, axis=0)
    data[:, 0] = data[:, 0] - means[0]
    data[:, 1] = data[:, 1] - means[1]
    return data

if __name__ == "__main__":
    from scipy import signal
    S = Sonar()
    S.connect()
    S.blink()
    S.build_charge()
    S.set_signal()
    for x in range(0,5):
        time.sleep(1)
        start = time.time()
        data = S.measure()
        data = convert_data(data)
    S.disconnect()
    f, t, sxx = signal.spectrogram(data[:, 0], 300, nperseg=64, noverlap=63)